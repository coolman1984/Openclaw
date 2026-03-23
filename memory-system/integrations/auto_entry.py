"""
Auto Entry Generator - Automatically generate entries from conversations
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4

from integrations.conversation_parser import ConversationParser, ConversationValidator
from models import Entry, Task, Decision, Blocker, Conversation, Summary
from database import Database


class AutoEntryGenerator:
    """Automatically generate entry from conversation context."""
    
    def __init__(self, parser: ConversationParser, database: Database):
        self.parser = parser
        self.db = database
        self.validator = ConversationValidator()
    
    def generate_from_conversation(self, 
                                   conversation_text: str,
                                   source: str = 'unknown',
                                   auto_create: bool = False,
                                   dry_run: bool = False) -> Dict[str, Any]:
        """Generate entry from conversation."""
        
        # Parse the conversation
        parsed = self.parser.parse(conversation_text, source)
        
        # Validate extractions
        valid_tasks = [t for t in parsed['tasks'] if self.validator.validate_task(t)]
        valid_decisions = [d for d in parsed['decisions'] if self.validator.validate_decision(d)]
        valid_blockers = [b for b in parsed['blockers'] if self.validator.validate_blocker(b)]
        
        # Create entry
        entry = self._create_entry(
            summary=parsed['summary'],
            tasks=valid_tasks,
            decisions=valid_decisions,
            blockers=valid_blockers,
            conversation=parsed
        )
        
        result = {
            'entry': entry.to_dict(),
            'extracted': {
                'tasks': len(valid_tasks),
                'decisions': len(valid_decisions),
                'blockers': len(valid_blockers)
            },
            'created': False,
            'pending_approval': False,
            'parse_id': None
        }
        
        if dry_run:
            return result
        
        if auto_create:
            # Save directly, merging into an existing same-day entry when present
            entry = self._merge_with_existing_entry(entry)
            self.db.save_entry(entry)
            result['created'] = True
        else:
            # Save to pending parses for approval
            parse_id = f"parse_{uuid4().hex[:8]}"
            self.db.save_pending_parse(
                parse_id=parse_id,
                source=source,
                raw_text=conversation_text,
                extracted_data={
                    'entry': entry.to_dict(),
                    'parsed': parsed
                }
            )
            result['pending_approval'] = True
            result['parse_id'] = parse_id
        
        return result
    
    def _create_entry(self,
                      summary: str,
                      tasks: List[Dict],
                      decisions: List[Dict],
                      blockers: List[Dict],
                      conversation: Dict) -> Entry:
        """Create entry from parsed data."""
        
        now = datetime.now().isoformat()
        date = datetime.now().strftime('%Y-%m-%d')
        
        # Create task objects
        task_objects = []
        task_ids = []
        for task_data in tasks:
            task = Task.create(
                title=task_data['title'],
                priority=task_data.get('priority', 'medium'),
                tags=['auto-extracted']
            )
            task.entry_date = date
            task_objects.append(task)
            task_ids.append(task.id)
        
        # Create decision objects
        decision_objects = []
        decision_ids = []
        for decision_data in decisions:
            alternatives = [
                {'option': alt, 'pros': [], 'cons': []}
                for alt in decision_data.get('alternatives', [])
            ]
            
            decision = Decision.create(
                title=decision_data['title'],
                context=decision_data.get('context', ''),
                decision=decision_data.get('decision', decision_data['title']),
                alternatives=alternatives,
                tags=['auto-extracted']
            )
            decision_objects.append(decision)
            decision_ids.append(decision.id)
        
        # Create blocker objects
        blocker_objects = []
        blocker_ids = []
        for blocker_data in blockers:
            blocker = Blocker.create(
                title=blocker_data['title'],
                description=blocker_data.get('description', ''),
                severity=blocker_data.get('severity', 'medium'),
                impact=blocker_data.get('impact', 'blocking'),
                tags=['auto-extracted']
            )
            blocker_objects.append(blocker)
            blocker_ids.append(blocker.id)
        
        # Create conversation record
        conversation_obj = Conversation.create(
            source=conversation['source'],
            summary=summary,
            raw_text='',  # Don't store full text to save space
            context_hash=conversation['context_hash'],
            extracted_tasks=task_ids,
            extracted_decisions=decision_ids,
            extracted_blockers=blocker_ids
        )
        
        # Create the entry
        entry = Entry(
            id=date,
            date=date,
            timestamp_created=now,
            timestamp_updated=now,
            version='1.0',
            summary=Summary(
                title=summary[:100],
                description=summary,
                mood='',
                energy_level=5
            ),
            tasks=task_objects,
            decisions=decision_objects,
            blockers=blocker_objects,
            conversations=[conversation_obj],
            tags=['auto-generated']
        )
        
        # Update metrics
        entry.metrics.tasks_created = len(task_objects)
        entry.metrics.decisions_made = len(decision_objects)
        entry.metrics.blockers_identified = len(blocker_objects)
        
        return entry
    
    def _merge_with_existing_entry(self, entry: Entry) -> Entry:
        """Merge auto-generated content into an existing same-day entry if one exists."""
        existing = self.db.get_entry(entry.date)
        if not existing:
            return entry

        def merge_unique(existing_items, new_items, key='id'):
            seen = {getattr(item, key, None) for item in existing_items}
            for item in new_items:
                value = getattr(item, key, None)
                if value not in seen:
                    existing_items.append(item)
                    seen.add(value)
            return existing_items

        existing.tasks = merge_unique(existing.tasks, entry.tasks)
        existing.decisions = merge_unique(existing.decisions, entry.decisions)
        existing.blockers = merge_unique(existing.blockers, entry.blockers)
        existing.conversations.extend(entry.conversations)
        existing.tags = sorted(set(existing.tags + entry.tags))
        existing.references = sorted(set(existing.references + entry.references))
        existing.timestamp_updated = datetime.now().isoformat()
        existing.metrics.tasks_created += entry.metrics.tasks_created
        existing.metrics.decisions_made += entry.metrics.decisions_made
        existing.metrics.blockers_identified += entry.metrics.blockers_identified
        return existing
    
    def approve_pending_parse(self, parse_id: str) -> bool:
        """Approve and create entry from pending parse."""
        # Get pending parse
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT extracted_data FROM pending_parses WHERE id = ?",
            (parse_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return False
        
        data = json.loads(row['extracted_data'])
        entry = Entry.from_dict(data['entry'])
        
        # Merge and save entry
        entry = self._merge_with_existing_entry(entry)
        self.db.save_entry(entry)
        
        # Mark as approved
        cursor.execute(
            "UPDATE pending_parses SET approved = 1 WHERE id = ?",
            (parse_id,)
        )
        self.db.conn.commit()
        
        return True
    
    def get_pending_parses(self) -> List[Dict[str, Any]]:
        """Get all pending parses."""
        return self.db.get_pending_parses()
    
    def preview_entry(self, conversation_text: str, source: str = 'unknown') -> str:
        """Generate a preview of what would be created."""
        result = self.generate_from_conversation(
            conversation_text,
            source=source,
            dry_run=True
        )
        
        lines = [
            "=" * 60,
            "AUTO-ENTRY PREVIEW",
            "=" * 60,
            "",
            f"Summary: {result['entry']['summary']['title']}",
            "",
            f"Tasks to create ({result['extracted']['tasks']}):",
        ]
        
        for task in result['entry']['tasks']:
            lines.append(f"  - [{task['priority']}] {task['title']}")
        
        lines.extend([
            "",
            f"Decisions to create ({result['extracted']['decisions']}):",
        ])
        
        for decision in result['entry']['decisions']:
            lines.append(f"  - {decision['title']}")
        
        lines.extend([
            "",
            f"Blockers to create ({result['extracted']['blockers']}):",
        ])
        
        for blocker in result['entry']['blockers']:
            lines.append(f"  - [{blocker['severity']}] {blocker['title']}")
        
        lines.extend([
            "",
            "=" * 60,
            "Use --auto-create to save this entry",
            "=" * 60,
        ])
        
        return "\n".join(lines)


class BatchEntryGenerator:
    """Generate entries from multiple conversations."""
    
    def __init__(self, generator: AutoEntryGenerator):
        self.generator = generator
    
    def batch_process(self, conversations: List[Dict[str, str]], 
                      auto_create: bool = False) -> Dict[str, Any]:
        """Process multiple conversations."""
        results = {
            'processed': 0,
            'created': 0,
            'pending': 0,
            'errors': []
        }
        
        for conv in conversations:
            try:
                result = self.generator.generate_from_conversation(
                    conversation_text=conv['text'],
                    source=conv.get('source', 'unknown'),
                    auto_create=auto_create
                )
                
                results['processed'] += 1
                if result['created']:
                    results['created'] += 1
                elif result['pending_approval']:
                    results['pending'] += 1
                    
            except Exception as e:
                results['errors'].append({
                    'source': conv.get('source', 'unknown'),
                    'error': str(e)
                })
        
        return results
