import os
import hashlib
import difflib
from typing import List, Dict, Any, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass
from pathlib import Path
import re
import json
from datetime import datetime

@dataclass
class DuplicateGroup:
    """Represents a group of duplicate files"""
    hash_signature: str
    files: List[Dict[str, Any]]
    duplicate_type: str  # 'exact', 'similar', 'name_based'
    confidence: float
    recommended_action: str

@dataclass
class CleanupAction:
    """Represents a recommended cleanup action"""
    action_type: str
    priority: str  # 'high', 'medium', 'low'
    description: str
    affected_files: List[str]
    estimated_time: int  # minutes
    automation_possible: bool

class AdvancedDataCleaner:
    """Enhanced data cleaner with advanced duplicate detection and cleanup suggestions"""
    
    def __init__(self):
        self.duplicate_threshold = 0.85
        self.similarity_threshold = 0.7
        self.name_similarity_threshold = 0.8
        
        # Common problematic patterns
        self.problematic_patterns = {
            'version_indicators': [
                r'_v\d+', r'_version_?\d+', r'_final', r'_copy', r'\(\d+\)',
                r'_new', r'_old', r'_backup', r'_draft', r'_revised'
            ],
            'generic_names': [
                r'^untitled\d*', r'^document\d*', r'^file\d*', r'^image\d*',
                r'^download\d*', r'^new folder\d*', r'^copy of'
            ],
            'system_generated': [
                r'^~\$', r'\.tmp$', r'\.temp$', r'^\.DS_Store$',
                r'Thumbs\.db$', r'desktop\.ini$'
            ]
        }
        
        # File extension categories for intelligent grouping
        self.extension_groups = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'videos': ['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
        }

    def clean_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhanced cleaning with comprehensive duplicate detection"""
        if not results:
            return []
        
        # Filter valid results
        valid_results = [r for r in results if r and r.get('status') == 'analyzed']
        
        # Enhance each result with additional metadata
        enhanced_results = []
        for result in valid_results:
            enhanced = self._enhance_file_metadata(result)
            enhanced_results.append(enhanced)
        
        return enhanced_results

    def detect_comprehensive_issues(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive issue detection with advanced algorithms"""
        issues = {
            'exact_duplicates': [],
            'similar_files': [],
            'naming_issues': {
                'untitled_files': [],
                'generic_names': [],
                'version_conflicts': [],
                'encoding_issues': [],
                'system_files': []
            },
            'size_anomalies': {
                'empty_files': [],
                'oversized_files': [],
                'suspicious_sizes': []
            },
            'temporal_issues': {
                'future_dates': [],
                'very_old_files': [],
                'rapid_duplicates': []
            }
        }
        
        # Detect exact duplicates
        issues['exact_duplicates'] = self._find_exact_duplicates(files)
        
        # Detect similar files
        issues['similar_files'] = self._find_similar_files(files)
        
        # Analyze naming patterns
        issues['naming_issues'] = self._analyze_naming_patterns(files)
        
        # Detect size anomalies
        issues['size_anomalies'] = self._detect_size_anomalies(files)
        
        # Detect temporal issues
        issues['temporal_issues'] = self._detect_temporal_issues(files)
        
        return issues

    def _enhance_file_metadata(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance file metadata with additional analysis"""
        enhanced = file_info.copy()
        
        filename = file_info.get('filename', '')
        file_path = file_info.get('path', '')
        
        # Add naming analysis
        enhanced['naming_analysis'] = self._analyze_filename(filename)
        
        # Add path depth
        enhanced['path_depth'] = len(Path(file_path).parts)
        
        # Add file age category
        enhanced['age_category'] = self._categorize_file_age(file_info.get('modified', 0))
        
        # Add extension group
        extension = file_info.get('extension', '').lower()
        enhanced['extension_group'] = self._get_extension_group(extension)
        
        return enhanced

    def _find_exact_duplicates(self, files: List[Dict[str, Any]]) -> List[DuplicateGroup]:
        """Find exact duplicates using multiple hash methods"""
        hash_groups = defaultdict(list)
        
        for file_info in files:
            similarity_hash = file_info.get('similarity_hash')
            if similarity_hash:
                hash_groups[similarity_hash].append(file_info)
        
        duplicate_groups = []
        for hash_val, file_list in hash_groups.items():
            if len(file_list) > 1:
                # Verify duplicates by additional checks
                verified_duplicates = self._verify_duplicates(file_list)
                if len(verified_duplicates) > 1:
                    group = DuplicateGroup(
                        hash_signature=hash_val,
                        files=verified_duplicates,
                        duplicate_type='exact',
                        confidence=1.0,
                        recommended_action=self._recommend_duplicate_action(verified_duplicates)
                    )
                    duplicate_groups.append(group)
        
        return duplicate_groups

    def _find_similar_files(self, files: List[Dict[str, Any]]) -> List[DuplicateGroup]:
        """Find similar files using name and content analysis"""
        similar_groups = []
        
        # Group by extension for efficiency
        extension_groups = defaultdict(list)
        for file_info in files:
            ext = file_info.get('extension', '').lower()
            extension_groups[ext].append(file_info)
        
        for ext, file_list in extension_groups.items():
            if len(file_list) > 1:
                similar_groups.extend(self._find_similar_within_group(file_list))
        
        return similar_groups

    def _find_similar_within_group(self, files: List[Dict[str, Any]]) -> List[DuplicateGroup]:
        """Find similar files within a group of same extension"""
        similar_groups = []
        processed = set()
        
        for i, file1 in enumerate(files):
            if i in processed:
                continue
                
            similar_files = [file1]
            
            for j, file2 in enumerate(files[i+1:], i+1):
                if j in processed:
                    continue
                
                similarity = self._calculate_file_similarity(file1, file2)
                if similarity > self.similarity_threshold:
                    similar_files.append(file2)
                    processed.add(j)
            
            if len(similar_files) > 1:
                processed.add(i)
                group = DuplicateGroup(
                    hash_signature=f"similar_{i}",
                    files=similar_files,
                    duplicate_type='similar',
                    confidence=self._calculate_group_confidence(similar_files),
                    recommended_action=self._recommend_similar_action(similar_files)
                )
                similar_groups.append(group)
        
        return similar_groups

    def _calculate_file_similarity(self, file1: Dict[str, Any], file2: Dict[str, Any]) -> float:
        """Calculate similarity score between two files using multiple factors"""
        scores = []
        
        # Name similarity
        name1 = file1.get('filename', '').lower()
        name2 = file2.get('filename', '').lower()
        name_sim = difflib.SequenceMatcher(None, name1, name2).ratio()
        scores.append(('name', name_sim, 0.4))
        
        # Size similarity (for non-empty files)
        size1 = file1.get('size', 0)
        size2 = file2.get('size', 0)
        if size1 > 0 and size2 > 0:
            size_ratio = min(size1, size2) / max(size1, size2)
            scores.append(('size', size_ratio, 0.2))
        
        # Extension match
        ext_match = 1.0 if file1.get('extension') == file2.get('extension') else 0.0
        scores.append(('extension', ext_match, 0.1))
        
        # Content similarity (if available)
        content1 = file1.get('content_text', '')
        content2 = file2.get('content_text', '')
        if content1 and content2:
            content_sim = difflib.SequenceMatcher(None, content1[:200], content2[:200]).ratio()
            scores.append(('content', content_sim, 0.3))
        
        # Calculate weighted score
        total_weight = sum(weight for _, _, weight in scores)
        if total_weight > 0:
            weighted_score = sum(score * weight for _, score, weight in scores) / total_weight
            return weighted_score
        
        return 0.0

    def _verify_duplicates(self, file_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verify duplicates using additional checks beyond hash"""
        if len(file_list) <= 1:
            return file_list
        
        # Group by size first
        size_groups = defaultdict(list)
        for file_info in file_list:
            size = file_info.get('size', 0)
            size_groups[size].append(file_info)
        
        verified = []
        for size, files in size_groups.items():
            if len(files) > 1:
                verified.extend(files)
        
        return verified

    def _analyze_naming_patterns(self, files: List[Dict[str, Any]]) -> Dict[str, List]:
        """Analyze files for naming pattern issues"""
        naming_issues = {
            'untitled_files': [],
            'generic_names': [],
            'version_conflicts': [],
            'encoding_issues': [],
            'system_files': []
        }
        
        for file_info in files:
            filename = file_info.get('filename', '').lower()
            
            # Check each pattern category
            if any(re.search(pattern, filename) for pattern in self.problematic_patterns['generic_names']):
                if 'untitled' in filename:
                    naming_issues['untitled_files'].append(file_info)
                else:
                    naming_issues['generic_names'].append(file_info)
            
            elif any(re.search(pattern, filename) for pattern in self.problematic_patterns['version_indicators']):
                naming_issues['version_conflicts'].append(file_info)
            
            elif any(re.search(pattern, filename) for pattern in self.problematic_patterns['system_generated']):
                naming_issues['system_files'].append(file_info)
            
            # Check for encoding issues
            try:
                filename.encode('ascii')
            except UnicodeEncodeError:
                naming_issues['encoding_issues'].append(file_info)
        
        return naming_issues

    def _detect_size_anomalies(self, files: List[Dict[str, Any]]) -> Dict[str, List]:
        """Detect files with unusual sizes"""
        size_issues = {
            'empty_files': [],
            'oversized_files': [],
            'suspicious_sizes': []
        }
        
        sizes = [f.get('size', 0) for f in files if f.get('size', 0) > 0]
        if not sizes:
            return size_issues
        
        # Calculate size statistics
        avg_size = sum(sizes) / len(sizes)
        max_reasonable_size = avg_size * 100  # 100x average
        
        for file_info in files:
            size = file_info.get('size', 0)
            
            if size == 0:
                size_issues['empty_files'].append(file_info)
            elif size > max_reasonable_size:
                size_issues['oversized_files'].append(file_info)
            elif self._is_suspicious_size(size, file_info.get('extension', '')):
                size_issues['suspicious_sizes'].append(file_info)
        
        return size_issues

    def _detect_temporal_issues(self, files: List[Dict[str, Any]]) -> Dict[str, List]:
        """Detect files with temporal anomalies"""
        temporal_issues = {
            'future_dates': [],
            'very_old_files': [],
            'rapid_duplicates': []
        }
        
        current_time = datetime.now().timestamp()
        very_old_threshold = current_time - (10 * 365 * 24 * 3600)  # 10 years
        
        # Group files by creation time for rapid duplicate detection
        time_groups = defaultdict(list)
        
        for file_info in files:
            created = file_info.get('created', 0)
            modified = file_info.get('modified', 0)
            
            # Future dates
            if created > current_time or modified > current_time:
                temporal_issues['future_dates'].append(file_info)
            
            # Very old files
            elif created < very_old_threshold:
                temporal_issues['very_old_files'].append(file_info)
            
            # Group by minute for rapid duplicate detection
            time_key = int(created // 60)  # Group by minute
            time_groups[time_key].append(file_info)
        
        # Find rapid duplicates (multiple files created within same minute)
        for time_key, time_files in time_groups.items():
            if len(time_files) > 3:  # More than 3 files in same minute
                temporal_issues['rapid_duplicates'].extend(time_files)
        
        return temporal_issues

    def _is_suspicious_size(self, size: int, extension: str) -> bool:
        """Check if file size is suspicious for its type"""
        ext_lower = extension.lower()
        
        # Very small sizes for file types that should be larger
        if size < 100:  # Less than 100 bytes
            if ext_lower in ['.jpg', '.png', '.pdf', '.docx', '.mp4']:
                return True
        
        # Exact common suspicious sizes (often corrupted downloads)
        suspicious_exact_sizes = [0, 1, 404, 1024, 2048]  # Common error sizes
        if size in suspicious_exact_sizes:
            return True
        
        return False

    def _analyze_filename(self, filename: str) -> Dict[str, Any]:
        """Analyze filename for various patterns and issues"""
        analysis = {
            'has_version_indicator': False,
            'is_generic_name': False,
            'is_system_file': False,
            'encoding_safe': True,
            'naming_score': 0.0,
            'suggestions': []
        }
        
        filename_lower = filename.lower()
        
        # Check for version indicators
        if any(re.search(pattern, filename_lower) for pattern in self.problematic_patterns['version_indicators']):
            analysis['has_version_indicator'] = True
            analysis['suggestions'].append('Consider consolidating versions')
        
        # Check for generic names
        if any(re.search(pattern, filename_lower) for pattern in self.problematic_patterns['generic_names']):
            analysis['is_generic_name'] = True
            analysis['suggestions'].append('Use more descriptive filename')
        
        # Check encoding
        try:
            filename.encode('ascii')
        except UnicodeEncodeError:
            analysis['encoding_safe'] = False
            analysis['suggestions'].append('Contains special characters that may cause issues')
        
        # Calculate naming score
        score = 100.0
        if analysis['has_version_indicator']:
            score -= 20
        if analysis['is_generic_name']:
            score -= 30
        if not analysis['encoding_safe']:
            score -= 10
        if len(filename) < 3:
            score -= 25
        
        analysis['naming_score'] = max(0, score)
        
        return analysis

    def _categorize_file_age(self, timestamp: float) -> str:
        """Categorize file by age"""
        if timestamp <= 0:
            return 'unknown'
        
        current_time = datetime.now().timestamp()
        age_days = (current_time - timestamp) / (24 * 3600)
        
        if age_days < 7:
            return 'recent'
        elif age_days < 30:
            return 'this_month'
        elif age_days < 365:
            return 'this_year'
        elif age_days < 365 * 3:
            return 'few_years'
        else:
            return 'old'

    def _get_extension_group(self, extension: str) -> str:
        """Get the group category for a file extension"""
        ext_lower = extension.lower()
        
        for group_name, extensions in self.extension_groups.items():
            if ext_lower in extensions:
                return group_name
        
        return 'other'

    def _recommend_duplicate_action(self, duplicates: List[Dict[str, Any]]) -> str:
        """Recommend action for duplicate files"""
        if len(duplicates) <= 1:
            return 'no_action'
        
        # Keep the newest file by default
        sorted_files = sorted(duplicates, key=lambda x: x.get('modified', 0), reverse=True)
        newest = sorted_files[0]
        
        # Check if any file has a better name
        for file_info in duplicates:
            naming_analysis = file_info.get('naming_analysis', {})
            if naming_analysis.get('naming_score', 0) > 70:
                return f"keep_best_named: {file_info['filename']}"
        
        return f"keep_newest: {newest['filename']}"

    def _recommend_similar_action(self, similar_files: List[Dict[str, Any]]) -> str:
        """Recommend action for similar files"""
        return "review_manually"

    def _calculate_group_confidence(self, files: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for a group of similar files"""
        if len(files) < 2:
            return 0.0
        
        # Calculate average pairwise similarity
        total_similarity = 0.0
        pairs = 0
        
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                similarity = self._calculate_file_similarity(files[i], files[j])
                total_similarity += similarity
                pairs += 1
        
        return total_similarity / pairs if pairs > 0 else 0.0

    def generate_cleanup_recommendations(self, issues: Dict[str, Any]) -> List[CleanupAction]:
        """Generate prioritized cleanup recommendations"""
        actions = []
        
        # High priority: Exact duplicates
        if issues.get('exact_duplicates'):
            total_duplicates = sum(len(group.files) - 1 for group in issues['exact_duplicates'])
            actions.append(CleanupAction(
                action_type='remove_exact_duplicates',
                priority='high',
                description=f"Remove {total_duplicates} exact duplicate files to save space",
                affected_files=[f['filename'] for group in issues['exact_duplicates'] for f in group.files[1:]],
                estimated_time=total_duplicates * 1,  # 1 minute per duplicate
                automation_possible=True
            ))
        
        # High priority: Empty files
        empty_files = issues.get('size_anomalies', {}).get('empty_files', [])
        if empty_files:
            actions.append(CleanupAction(
                action_type='remove_empty_files',
                priority='high',
                description=f"Remove {len(empty_files)} empty files",
                affected_files=[f['filename'] for f in empty_files],
                estimated_time=len(empty_files) * 0.5,
                automation_possible=True
            ))
        
        # Medium priority: Generic names
        untitled_files = issues.get('naming_issues', {}).get('untitled_files', [])
        if untitled_files:
            actions.append(CleanupAction(
                action_type='rename_generic_files',
                priority='medium',
                description=f"Rename {len(untitled_files)} files with generic names",
                affected_files=[f['filename'] for f in untitled_files],
                estimated_time=len(untitled_files) * 2,
                automation_possible=False
            ))
        
        # Medium priority: Version conflicts
        version_conflicts = issues.get('naming_issues', {}).get('version_conflicts', [])
        if version_conflicts:
            actions.append(CleanupAction(
                action_type='consolidate_versions',
                priority='medium',
                description=f"Review and consolidate {len(version_conflicts)} files with version indicators",
                affected_files=[f['filename'] for f in version_conflicts],
                estimated_time=len(version_conflicts) * 3,
                automation_possible=False
            ))
        
        # Low priority: Similar files
        similar_groups = issues.get('similar_files', [])
        if similar_groups:
            total_similar = sum(len(group.files) for group in similar_groups)
            actions.append(CleanupAction(
                action_type='review_similar_files',
                priority='low',
                description=f"Review {total_similar} potentially similar files in {len(similar_groups)} groups",
                affected_files=[f['filename'] for group in similar_groups for f in group.files],
                estimated_time=len(similar_groups) * 5,
                automation_possible=False
            ))
        
        return sorted(actions, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x.priority], reverse=True)

    def export_cleanup_report(self, issues: Dict[str, Any], recommendations: List[CleanupAction]) -> str:
        """Export detailed cleanup report as JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_issues': sum(
                    len(group) if isinstance(group, list) else 
                    sum(len(sublist) for sublist in group.values()) if isinstance(group, dict) else 0
                    for group in issues.values()
                ),
                'high_priority_actions': len([a for a in recommendations if a.priority == 'high']),
                'automation_possible': len([a for a in recommendations if a.automation_possible])
            },
            'detailed_issues': issues,
            'recommendations': [
                {
                    'action_type': action.action_type,
                    'priority': action.priority,
                    'description': action.description,
                    'affected_file_count': len(action.affected_files),
                    'estimated_time_minutes': action.estimated_time,
                    'automation_possible': action.automation_possible
                }
                for action in recommendations
            ]
        }
        
        return json.dumps(report, indent=2, default=str)