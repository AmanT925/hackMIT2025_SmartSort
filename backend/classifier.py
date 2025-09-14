"""
File classification and emotion analysis utilities
"""
import os
import random
from typing import Dict, Any, List
from pathlib import Path

def classify_file(file_path: str) -> Dict[str, Any]:
    """
    Classify a file based on its name, extension, and content
    """
    filename = os.path.basename(file_path)
    extension = Path(file_path).suffix.lower()
    
    # Basic classification categories
    categories = {
        'school': {
            'keywords': ['homework', 'assignment', 'essay', 'study', 'notes', 'midterm', 'final', 'quiz'],
            'extensions': ['.pdf', '.docx', '.txt']
        },
        'work': {
            'keywords': ['meeting', 'presentation', 'report', 'proposal', 'contract', 'budget'],
            'extensions': ['.pptx', '.xlsx', '.pdf', '.docx']
        },
        'financial': {
            'keywords': ['invoice', 'receipt', 'bill', 'tax', 'statement', 'payment', 'bank'],
            'extensions': ['.pdf', '.jpg', '.png']
        },
        'personal': {
            'keywords': ['vacation', 'family', 'birthday', 'wedding', 'photo', 'memory'],
            'extensions': ['.jpg', '.png', '.mp4', '.mov']
        },
        'media': {
            'keywords': ['photo', 'video', 'music', 'image', 'screenshot'],
            'extensions': ['.jpg', '.png', '.mp4', '.mp3', '.mov', '.avi']
        },
        'code': {
            'keywords': ['script', 'app', 'main', 'index', 'component'],
            'extensions': ['.py', '.js', '.html', '.css', '.java', '.cpp']
        }
    }
    
    filename_lower = filename.lower()
    scores = {}
    
    # Calculate scores for each category
    for category, criteria in categories.items():
        score = 0
        
        # Check keywords in filename
        for keyword in criteria['keywords']:
            if keyword in filename_lower:
                score += 2
        
        # Check file extension
        if extension in criteria['extensions']:
            score += 1
        
        scores[category] = score
    
    # Find best match
    best_category = max(scores, key=scores.get) if max(scores.values()) > 0 else 'uncategorized'
    confidence = scores[best_category] / 3.0  # Normalize to 0-1
    
    return {
        'category': best_category,
        'confidence': min(confidence, 1.0),
        'scores': scores,
        'filename': filename,
        'extension': extension
    }

def roast_emotion_analysis(directory_path: str = None) -> Dict[str, Any]:
    """
    Analyze file organization and provide humorous roasting commentary
    """
    if not directory_path:
        directory_path = os.getcwd()
    
    try:
        files = []
        for root, dirs, filenames in os.walk(directory_path):
            for filename in filenames:
                if not filename.startswith('.'):
                    files.append(filename)
        
        if not files:
            return {
                'roast': "Wow, your folder is so empty, even Marie Kondo would be concerned. Did you delete everything or are you just getting started?",
                'emotion': 'confused',
                'score': 0
            }
        
        # Analyze file naming patterns
        issues = []
        untitled_count = sum(1 for f in files if 'untitled' in f.lower())
        copy_count = sum(1 for f in files if 'copy' in f.lower() or '(1)' in f)
        final_count = sum(1 for f in files if 'final' in f.lower())
        screenshot_count = sum(1 for f in files if 'screenshot' in f.lower() or 'screen shot' in f.lower())
        
        roasts = []
        
        if untitled_count > 5:
            roasts.append(f"You have {untitled_count} 'Untitled' files. Are you allergic to creativity or just naming things in general?")
        
        if copy_count > 3:
            roasts.append(f"I see {copy_count} files with 'copy' in the name. Someone's been hitting Ctrl+C like it's going out of style!")
        
        if final_count > 2:
            roasts.append(f"You have {final_count} 'final' files. We both know none of them are actually final, don't we?")
        
        if screenshot_count > 10:
            roasts.append(f"With {screenshot_count} screenshots, your desktop looks like a digital hoarder's paradise!")
        
        if len(files) > 100:
            roasts.append("Your folder has more files than a government conspiracy theory. Time for some spring cleaning!")
        
        # Generate overall roast
        if not roasts:
            main_roast = "Your file organization is surprisingly decent. I'm almost disappointed - I was ready to roast you!"
            emotion = 'impressed'
            score = 8
        else:
            main_roast = random.choice(roasts)
            emotion = 'sassy'
            score = max(3, 10 - len(roasts))
        
        return {
            'roast': main_roast,
            'emotion': emotion,
            'score': score,
            'issues_found': len(roasts),
            'total_files': len(files),
            'detailed_issues': roasts
        }
        
    except Exception as e:
        return {
            'roast': f"I can't even analyze your mess because of this error: {str(e)}. That's... actually impressive.",
            'emotion': 'frustrated',
            'score': 1
        }

def analyze_file_patterns(files: List[str]) -> Dict[str, Any]:
    """
    Analyze patterns in file names for organization insights
    """
    patterns = {
        'version_indicators': 0,
        'generic_names': 0,
        'date_patterns': 0,
        'duplicate_indicators': 0
    }
    
    for filename in files:
        filename_lower = filename.lower()
        
        # Check for version indicators
        version_words = ['v1', 'v2', 'final', 'draft', 'copy', 'new', 'old']
        if any(word in filename_lower for word in version_words):
            patterns['version_indicators'] += 1
        
        # Check for generic names
        generic_words = ['untitled', 'document', 'file', 'new folder']
        if any(word in filename_lower for word in generic_words):
            patterns['generic_names'] += 1
        
        # Check for duplicate indicators
        if '(1)' in filename or 'copy of' in filename_lower:
            patterns['duplicate_indicators'] += 1
    
    return patterns
