"""
Conversation Parser - Extract structured data from conversation text
"""

import re
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime


class ConversationParser:
    """Parse conversation context and extract structured data."""
    
    def __init__(self, nlp_backend: str = 'regex'):
        self.nlp_backend = nlp_backend
        
        # Task extraction patterns
        self.task_patterns = [
            # Explicit markers
            (r'(?:TODO|FIXME|TASK|NEED TO|HAVE TO|MUST)\s*:?\s*(.+?)(?=\n|$)', 'high'),
            # Checkbox style
            (r'(?:\-|\*|\d+\.)\s*\[\s*\]\s*(.+?)(?=\n|$)', 'medium'),
            # Action items
            (r'(?:action item|follow.up|next step)\s*:?\s*(.+?)(?=\n|$)', 'medium'),
            # Start with verb
            (r'(?:^|\n)(?:Create|Build|Implement|Fix|Update|Add|Remove|Refactor|Test|Deploy)\s+(.+?)(?=\n|$)', 'medium'),
        ]
        
        # Decision extraction patterns
        self.decision_patterns = [
            # Explicit markers
            (r'(?:DECIDED|DECISION|CHOSEN|WILL USE|WENT WITH)\s*:?\s*(.+?)(?=\n|$)', 'high'),
            # Decision phrases
            (r'(?:we decided|I decided|let\'s go with|we\'ll use|we chose)\s+(?:to\s+)?(.+?)(?=\n|$)', 'high'),
            # Architecture choices
            (r'(?:architecture|design|approach)\s*:?\s*(.+?)(?=\n|$)', 'medium'),
        ]
        
        # Blocker extraction patterns
        self.blocker_patterns = [
            # Explicit markers
            (r'(?:BLOCKED|BLOCKER|STUCK|ISSUE|PROBLEM)\s*:?\s*(.+?)(?=\n|$)', 'high'),
            # Can't proceed
            (r'(?:can\'t|cannot|unable to|blocked from)\s+(?:proceed|continue|move forward|complete)\s*(?:because|due to|by)?\s*(.+?)(?=\n|$)', 'high'),
            # Waiting on
            (r'(?:waiting on|blocked by|depends on|need from)\s+(.+?)(?=\n|$)', 'high'),
            # Problem statements
            (r'(?:problem|issue|error|bug|failure)\s*:?\s*(.+?)(?=\n|$)', 'medium'),
        ]
        
        # Summary generation patterns
        self.sentence_endings = re.compile(r'[.!?]+\s+')
    
    def parse(self, text: str, source: str = 'unknown') -> Dict[str, Any]:
        """Parse conversation text and return structured data."""
        return {
            'tasks': self.extract_tasks(text),
            'decisions': self.extract_decisions(text),
            'blockers': self.extract_blockers(text),
            'summary': self.generate_summary(text),
            'context_hash': self.compute_hash(text),
            'source': source,
            'timestamp': datetime.now().isoformat()
        }
    
    def extract_tasks(self, text: str) -> List[Dict[str, Any]]:
        """Extract task items from text."""
        tasks = []
        seen = set()
        
        for pattern, confidence_level in self.task_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                task_text = match.group(1).strip()
                
                # Deduplicate
                task_key = task_text.lower()[:50]
                if task_key in seen:
                    continue
                seen.add(task_key)
                
                # Extract priority if mentioned
                priority = self._extract_priority(task_text)
                
                # Clean up task text
                task_text = self._clean_text(task_text)
                
                tasks.append({
                    'title': task_text,
                    'source_text': match.group(0).strip(),
                    'confidence': confidence_level,
                    'priority': priority,
                    'extracted_at': datetime.now().isoformat()
                })
        
        return tasks
    
    def extract_decisions(self, text: str) -> List[Dict[str, Any]]:
        """Extract decision items from text."""
        decisions = []
        seen = set()
        
        for pattern, confidence_level in self.decision_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                decision_text = match.group(1).strip()
                
                # Deduplicate
                decision_key = decision_text.lower()[:50]
                if decision_key in seen:
                    continue
                seen.add(decision_key)
                
                # Extract context (surrounding text)
                context = self._extract_context(text, match.start(), match.end())
                
                # Look for alternatives
                alternatives = self._extract_alternatives(text, match.start())
                
                decisions.append({
                    'title': decision_text[:100],
                    'decision': decision_text,
                    'context': context,
                    'alternatives': alternatives,
                    'source_text': match.group(0).strip(),
                    'confidence': confidence_level,
                    'extracted_at': datetime.now().isoformat()
                })
        
        return decisions
    
    def extract_blockers(self, text: str) -> List[Dict[str, Any]]:
        """Extract blocker items from text."""
        blockers = []
        seen = set()
        
        for pattern, confidence_level in self.blocker_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                blocker_text = match.group(1).strip()
                
                # Deduplicate
                blocker_key = blocker_text.lower()[:50]
                if blocker_key in seen:
                    continue
                seen.add(blocker_key)
                
                # Extract severity
                severity = self._extract_severity(blocker_text)
                
                # Extract impact
                impact = self._extract_impact(blocker_text)
                
                blockers.append({
                    'title': blocker_text[:100],
                    'description': blocker_text,
                    'severity': severity,
                    'impact': impact,
                    'source_text': match.group(0).strip(),
                    'confidence': confidence_level,
                    'extracted_at': datetime.now().isoformat()
                })
        
        return blockers
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate conversation summary."""
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]*`', '', text)
        
        # Get first paragraph or sentences
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if paragraphs:
            first_para = paragraphs[0]
            if len(first_para) <= max_length:
                return first_para
            
            # Truncate to complete sentences
            sentences = self.sentence_endings.split(first_para)
            summary = sentences[0]
            for sentence in sentences[1:]:
                if len(summary) + len(sentence) + 1 <= max_length:
                    summary += '. ' + sentence
                else:
                    break
            
            return summary + ('...' if len(first_para) > max_length else '')
        
        return text[:max_length].strip() + ('...' if len(text) > max_length else '')
    
    def compute_hash(self, text: str) -> str:
        """Compute hash of text for deduplication."""
        return f"sha256:{hashlib.sha256(text.encode()).hexdigest()[:16]}"
    
    def _extract_priority(self, text: str) -> str:
        """Extract priority from task text."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['urgent', 'asap', 'critical', 'blocking']):
            return 'high'
        elif any(word in text_lower for word in ['important', 'should', 'need']):
            return 'medium'
        return 'low'
    
    def _extract_severity(self, text: str) -> str:
        """Extract severity from blocker text."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'down', 'broken', 'crash']):
            return 'critical'
        elif any(word in text_lower for word in ['high', 'urgent', 'blocking']):
            return 'high'
        elif any(word in text_lower for word in ['medium', 'issue', 'problem']):
            return 'medium'
        return 'low'
    
    def _extract_impact(self, text: str) -> str:
        """Extract impact from blocker text."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['completely', 'totally', 'cannot proceed']):
            return 'blocking'
        elif any(word in text_lower for word in ['slow', 'workaround', 'delay']):
            return 'moderate'
        return 'minor'
    
    def _extract_context(self, text: str, match_start: int, match_end: int, 
                         window: int = 200) -> str:
        """Extract surrounding context."""
        start = max(0, match_start - window)
        end = min(len(text), match_end + window)
        
        context = text[start:end].strip()
        
        # Add ellipses if truncated
        if start > 0:
            context = '...' + context
        if end < len(text):
            context = context + '...'
        
        return context
    
    def _extract_alternatives(self, text: str, match_pos: int) -> List[str]:
        """Extract alternatives mentioned near a decision."""
        # Look for patterns like "A vs B", "A or B", "A instead of B"
        window = text[max(0, match_pos - 300):match_pos + 300]
        
        alternatives = []
        
        # Pattern: X vs Y, X or Y
        vs_pattern = re.findall(r'(\w+)\s+(?:vs|versus|or)\s+(\w+)', window, re.IGNORECASE)
        for a, b in vs_pattern:
            alternatives.extend([a, b])
        
        # Pattern: instead of X, we chose Y
        instead_pattern = re.findall(r'instead of\s+(\w+)', window, re.IGNORECASE)
        alternatives.extend(instead_pattern)
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for alt in alternatives:
            alt_lower = alt.lower()
            if alt_lower not in seen:
                seen.add(alt_lower)
                unique.append(alt)
        
        return unique[:5]  # Limit to 5 alternatives
    
    def _clean_text(self, text: str) -> str:
        """Clean up extracted text."""
        # Remove markdown
        text = re.sub(r'\*\*?|\_\_?', '', text)
        # Remove URLs
        text = re.sub(r'https?://\S+', '[link]', text)
        # Clean whitespace
        text = ' '.join(text.split())
        return text.strip()


class ConversationValidator:
    """Validate extracted conversation data."""
    
    @staticmethod
    def validate_task(task: Dict) -> bool:
        """Validate task extraction."""
        if not task.get('title'):
            return False
        if len(task['title']) < 3:
            return False
        return True
    
    @staticmethod
    def validate_decision(decision: Dict) -> bool:
        """Validate decision extraction."""
        if not decision.get('title'):
            return False
        if len(decision['title']) < 5:
            return False
        return True
    
    @staticmethod
    def validate_blocker(blocker: Dict) -> bool:
        """Validate blocker extraction."""
        if not blocker.get('title'):
            return False
        if len(blocker['title']) < 5:
            return False
        return True
