import random
from typing import Dict, Any

class VoiceHandler:
    def __init__(self):
        print("Voice handler initialized")
        self.roast_templates = [
            "Your file organization is... creative. Let's call it that.",
            "I see you're a fan of the 'everything goes everywhere' filing system!",
            "Your Downloads folder called - it wants a restraining order.",
            "You have way too many files named 'Untitled' - we need to talk!"
        ]
    
    def process_command(self, text: str, file_analyzer=None) -> Dict[str, Any]:
        text_lower = text.lower()
        
        if "sort" in text_lower or "organize" in text_lower:
            return {
                "action": "sort",
                "response": "Starting to sort your files! Let me analyze everything first..."
            }
        elif "roast" in text_lower:
            return {
                "action": "roast",
                "response": random.choice(self.roast_templates)
            }
        elif "find" in text_lower:
            topic = self.extract_search_topic(text)
            return {
                "action": "find",
                "response": f"Searching for files related to '{topic}'...",
                "topic": topic
            }
        elif "tell me" in text_lower or "what" in text_lower:
            return {
                "action": "summarize",
                "response": "Let me tell you what I found in your files..."
            }
        else:
            return {
                "action": "help",
                "response": "I can sort folders, roast your organization, find files, or tell you what I found!"
            }
    
    def extract_search_topic(self, text: str) -> str:
        words = text.lower().split()
        if "about" in words:
            try:
                return words[words.index("about") + 1]
            except IndexError:
                pass
        if "for" in words:
            try:
                return words[words.index("for") + 1]
            except IndexError:
                pass
        return "unknown"
