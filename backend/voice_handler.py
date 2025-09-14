import tempfile
from queue import Queue
import sounddevice as sd
import soundfile as sf
from openai import OpenAI
from gtts import gTTS
import os

from fileSorter import sortFiles, findFiles, showDuplicates, undoLast
from classifier import classify_file, roast_emotion_analysis
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

class VoiceHandler:
    """Voice command processing handler"""
    
    def __init__(self):
        self.client = OpenAI()
        self.conversation_context = {}
    
    def process_command(self, command_text: str, analyzer=None) -> dict:
        """Process voice command using AI interpretation for flexible understanding"""
        
        # Use OpenAI GPT to intelligently interpret the voice command
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a voice command interpreter for a file organization system. 
                        Analyze the user's spoken command and determine their intent.
                        
                        Available actions:
                        - "sort": User wants to organize/sort/categorize files (e.g., "sort files", "organize this", "clean up folder", "arrange documents")
                        - "search": User wants to find files about a topic (e.g., "find files about X", "search for Y", "locate documents containing Z")
                        - "duplicates": User wants to find duplicate files (e.g., "show duplicates", "find copies", "duplicate files")
                        - "undo": User wants to undo the last action (e.g., "undo that", "reverse last action", "go back")
                        - "roast": User wants analysis/roasting of their organization (e.g., "roast my files", "analyze organization", "how messy are my files")
                        - "help": User wants help or instructions (e.g., "help", "what can you do", "commands")
                        - "unknown": Command doesn't match any available actions
                        
                        For search commands, also extract the search topic.
                        
                        Respond with a JSON object containing:
                        {
                            "action": "sort|search|duplicates|undo|roast|help|unknown",
                            "confidence": 0.0-1.0,
                            "topic": "extracted topic for search commands, null otherwise",
                            "reasoning": "brief explanation of why you chose this action"
                        }
                        
                        Examples:
                        - "sort my files" -> {"action": "sort", "confidence": 0.95, "topic": null, "reasoning": "Direct request to sort files"}
                        - "organize these documents" -> {"action": "sort", "confidence": 0.9, "topic": null, "reasoning": "Organize is synonymous with sort"}
                        - "find files about cats" -> {"action": "search", "confidence": 0.95, "topic": "cats", "reasoning": "Clear search request with topic"}
                        - "duplicate some files" -> {"action": "duplicates", "confidence": 0.8, "topic": null, "reasoning": "Likely wants to find duplicate files"}
                        - "what's the weather" -> {"action": "unknown", "confidence": 0.95, "topic": null, "reasoning": "Not related to file organization"}
                        """
                    },
                    {
                        "role": "user", 
                        "content": f"User said: '{command_text}'"
                    }
                ],
                temperature=0.1
            )
            
            import json
            ai_response = json.loads(completion.choices[0].message.content)
            action = ai_response.get("action", "unknown")
            confidence = ai_response.get("confidence", 0.0)
            topic = ai_response.get("topic")
            reasoning = ai_response.get("reasoning", "")
            
            # Execute the appropriate action based on AI interpretation
            if action == "sort":
                result = sortFiles()
                response = {
                    "action": "sort",
                    "message": f"Files organized successfully! Moved {result.get('files_moved', 0)} files. {reasoning}",
                    "result": result,
                    "confidence": confidence
                }
            
            elif action == "search":
                if not topic:
                    topic = self._extract_topic_fallback(command_text)
                files = findFiles(topic)
                response = {
                    "action": "search",
                    "message": f"Found {len(files)} files about '{topic}'. {reasoning}",
                    "files": files,
                    "topic": topic,
                    "confidence": confidence
                }
            
            elif action == "duplicates":
                duplicates = showDuplicates()
                response = {
                    "action": "duplicates",
                    "message": f"Found {len(duplicates)} groups of duplicate files. {reasoning}",
                    "duplicates": duplicates,
                    "confidence": confidence
                }
            
            elif action == "undo":
                result = undoLast()
                response = {
                    "action": "undo",
                    "message": f"{result.get('message', 'Undo operation completed')}. {reasoning}",
                    "result": result,
                    "confidence": confidence
                }
            
            elif action == "roast":
                roast_result = roast_emotion_analysis()
                response = {
                    "action": "roast",
                    "message": f"{roast_result.get('roast', 'Your files are... interesting.')} {reasoning}",
                    "emotion": roast_result.get('emotion', 'neutral'),
                    "score": roast_result.get('score', 5),
                    "confidence": confidence
                }
            
            elif action == "help":
                response = {
                    "action": "help",
                    "message": f"I can help you organize files! {reasoning}",
                    "commands": [
                        "sort files / organize documents / clean up folder",
                        "find files about [topic] / search for [topic]",
                        "show duplicates / find copies",
                        "undo that / reverse last action",
                        "roast my organization / analyze my files"
                    ],
                    "confidence": confidence
                }
            
            else:
                response = {
                    "action": "unknown",
                    "message": f"I heard '{command_text}' but I'm not sure how to help with that. Try asking me to 'sort files' or 'find duplicates'. {reasoning}",
                    "confidence": confidence
                }
                
        except Exception as ai_error:
            print(f"AI processing failed, falling back to simple matching: {ai_error}")
            # Fallback to enhanced keyword matching if AI fails
            response = self._fallback_command_processing(command_text)
        
        return response
    
    def _extract_topic_fallback(self, command: str) -> str:
        """Fallback method to extract topic from search command"""
        if "about" in command:
            return command.split("about")[-1].strip()
        elif "for" in command:
            return command.split("for")[-1].strip()
        else:
            # Fallback: return last word
            words = command.split()
            return words[-1] if words else "files"
    
    def _fallback_command_processing(self, command_text: str) -> dict:
        """Enhanced fallback command processing with broader keyword matching"""
        cmd = command_text.lower()
        
        # More flexible keyword matching
        if any(word in cmd for word in ["sort", "organize", "clean", "arrange", "tidy"]):
            result = sortFiles()
            return {
                "action": "sort",
                "message": f"Files organized successfully! Moved {result.get('files_moved', 0)} files.",
                "result": result
            }
        
        elif any(word in cmd for word in ["find", "search", "locate", "look"]) and any(word in cmd for word in ["about", "for", "containing"]):
            topic = self._extract_topic_fallback(cmd)
            files = findFiles(topic)
            return {
                "action": "search",
                "message": f"Found {len(files)} files about '{topic}'",
                "files": files,
                "topic": topic
            }
        
        elif any(word in cmd for word in ["duplicate", "copies", "same", "identical"]):
            duplicates = showDuplicates()
            return {
                "action": "duplicates",
                "message": f"Found {len(duplicates)} groups of duplicate files",
                "duplicates": duplicates
            }
        
        elif any(word in cmd for word in ["undo", "reverse", "back", "cancel"]):
            result = undoLast()
            return {
                "action": "undo",
                "message": result.get('message', 'Undo operation completed'),
                "result": result
            }
        
        elif any(word in cmd for word in ["roast", "analyze", "messy", "chaos", "organization"]):
            roast_result = roast_emotion_analysis()
            return {
                "action": "roast",
                "message": roast_result.get('roast', 'Your files are... interesting.'),
                "emotion": roast_result.get('emotion', 'neutral'),
                "score": roast_result.get('score', 5)
            }
        
        elif any(word in cmd for word in ["help", "commands", "what", "how"]):
            return {
                "action": "help",
                "message": "Available commands: sort files, find files about [topic], show duplicates, undo, roast my organization",
                "commands": [
                    "sort files / organize documents / clean up folder",
                    "find files about [topic] / search for [topic]",
                    "show duplicates / find copies",
                    "undo that / reverse last action",
                    "roast my organization / analyze my files"
                ]
            }
        
        return {
            "action": "unknown",
            "message": f"I heard '{command_text}' but I'm not sure how to help with that. Try asking me to 'sort files' or 'find duplicates'."
        }

conversation_context = {}


def record_audio(duration=5, fs=16000):
    q = Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status)
        q.put(indata.copy())

    print("🎤 Recording...")
    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        frames = []
        for _ in range(int(duration * fs / 1024)):
            frames.append(q.get())
    print("✅ Done recording")

    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with sf.SoundFile(tmpfile.name, mode='x', samplerate=fs,
                      channels=1, subtype="PCM_16") as f:
        for frame in frames:
            f.write(frame)
    return tmpfile.name


def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

def speak_response(text):
    tts = gTTS(text=text, lang='en')
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmpfile.name)
    os.system(f"start {tmpfile.name}")  # Windows. Use "afplay" on Mac or "mpg123" on Linux


def handle_command(text, user_id="default"):
    cmd = text.lower()
    response = "Command not recognized."

    if "sort this folder" in cmd:
        sortFiles()
        response = "Folder sorted."
        conversation_context[user_id] = {"last_action": "sort"}

    elif "find files about" in cmd:
        topic = cmd.split("about")[-1].strip()
        findFiles(topic)
        response = f"Searching files about {topic}"
        conversation_context[user_id] = {"last_action": "search", "topic": topic}

    elif "show me duplicates" in cmd:
        showDuplicates()
        response = "Here are the duplicate files."
        conversation_context[user_id] = {"last_action": "duplicates"}

    elif "undo that" in cmd:
        undoLast()
        response = "Undid the last action."
        conversation_context[user_id] = {"last_action": "undo"}

    elif "roast my organization" in cmd:
        roast_emotion_analysis()
        response = "Analyzing your folder chaos..."
        conversation_context[user_id] = {"last_action": "roast"}

    elif "repeat last" in cmd and user_id in conversation_context:
        last = conversation_context[user_id]["last_action"]
        response = f"Repeating your last action: {last}"

    speak_response(response)
    return response

def start_voice_control(user_id="default"):
    audio_path = record_audio()
    text = transcribe_audio(audio_path)
    print(f"🗣️ You said: {text}")
    response = handle_command(text, user_id)
    print(f"🤖 {response}")
    return response
