from typing import List, Dict, Any
from collections import defaultdict

class MessyDataCleaner:
    def __init__(self):
        self.duplicate_threshold = 0.95
    
    def clean_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []
        for result in results:
            if result and isinstance(result, dict):
                cleaned.append(result)
        return cleaned
    
    def detect_issues(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        issues = {
            'untitled_files': [],
            'generic_names': [],
            'version_conflicts': [],
            'duplicate_names': []
        }
        
        filename_counts = defaultdict(int)
        
        for file_info in files:
            filename = file_info.get('filename', '').lower()
            base_name = filename.split('.')[0]
            filename_counts[base_name] += 1
            
            if 'untitled' in filename:
                issues['untitled_files'].append(file_info)
            
            if filename in ['document.pdf', 'image.jpg', 'file.txt']:
                issues['generic_names'].append(file_info)
            
            if any(indicator in filename for indicator in ['final', 'v2', 'copy', '(1)']):
                issues['version_conflicts'].append(file_info)
        
        # Find duplicate names
        for base_name, count in filename_counts.items():
            if count > 1:
                matching_files = [f for f in files if f.get('filename', '').lower().startswith(base_name)]
                issues['duplicate_names'].extend(matching_files)
        
        return issues
    
    def suggest_cleanup_actions(self, issues: Dict[str, Any]) -> List[Dict[str, Any]]:
        suggestions = []
        
        if issues['untitled_files']:
            suggestions.append({
                'priority': 'high',
                'action': 'rename_untitled',
                'description': f"Rename {len(issues['untitled_files'])} 'Untitled' files",
                'affected_files': len(issues['untitled_files'])
            })
        
        if issues['version_conflicts']:
            suggestions.append({
                'priority': 'medium',
                'action': 'consolidate_versions',
                'description': f"Review {len(issues['version_conflicts'])} files with version conflicts",
                'affected_files': len(issues['version_conflicts'])
            })
        
        return suggestions
