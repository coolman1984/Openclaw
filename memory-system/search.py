"""
Search Engine with SQLite FTS Support
"""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from database import Database
from models import Entry, Task, Decision, Blocker
from utils import Colors, truncate


class SearchEngine:
    """Full-text search engine for memory data."""
    
    def __init__(self, database: Database):
        self.db = database
    
    def search(self, 
               query: Optional[str] = None,
               type: str = 'all',
               project: Optional[str] = None,
               from_date: Optional[str] = None,
               to: Optional[str] = None,
               tags: Optional[List[str]] = None,
               limit: int = 20,
               advanced: bool = False) -> Dict[str, List[Any]]:
        """Search across all memory data."""
        results = {
            'entries': [],
            'tasks': [],
            'decisions': [],
            'blockers': []
        }
        
        # Search entries (with FTS if available)
        if type in ['all', 'entry'] and query:
            if advanced:
                results['entries'] = self._search_entries_fts(query, limit)
            else:
                results['entries'] = self._search_entries_simple(query, limit)
        
        # Search tasks
        if type in ['all', 'task']:
            results['tasks'] = self._search_tasks(query, project, from_date, to, tags, limit)
        
        # Search decisions
        if type in ['all', 'decision']:
            results['decisions'] = self._search_decisions(query, project, limit)
        
        # Search blockers
        if type in ['all', 'blocker']:
            results['blockers'] = self._search_blockers(query, project, limit)
        
        # Apply common filters
        if project or from_date or to or tags:
            results = self._apply_filters(results, project, from_date, to, tags)
        
        return results
    
    def _search_entries_fts(self, query: str, limit: int) -> List[Entry]:
        """Search entries using SQLite FTS."""
        try:
            entries_data = self.db.search_entries_fts(query, limit)
            return [Entry.from_dict(data) for data in entries_data]
        except Exception:
            # Fall back to simple search if FTS fails
            return self._search_entries_simple(query, limit)
    
    def _search_entries_simple(self, query: str, limit: int) -> List[Entry]:
        """Simple text search in entries."""
        query_lower = query.lower()
        entries = self.db.list_entries(limit=limit * 2)  # Get more to filter
        
        results = []
        for entry in entries:
            # Search in various fields
            searchable_text = " ".join([
                entry.summary.title or "",
                entry.summary.description or "",
                " ".join(entry.tags),
                json.dumps(entry.to_dict())
            ]).lower()
            
            if query_lower in searchable_text:
                results.append(entry)
                if len(results) >= limit:
                    break
        
        return results
    
    def _search_tasks(self, 
                      query: Optional[str],
                      project: Optional[str],
                      from_date: Optional[str],
                      to: Optional[str],
                      tags: Optional[List[str]],
                      limit: int) -> List[Task]:
        """Search tasks."""
        tasks = self.db.list_tasks(limit=limit * 2)
        
        if query:
            query_lower = query.lower()
            tasks = [t for t in tasks if 
                     query_lower in t.title.lower() or 
                     query_lower in (t.description or "").lower()]
        
        return tasks[:limit]
    
    def _search_decisions(self, 
                          query: Optional[str],
                          project: Optional[str],
                          limit: int) -> List[Decision]:
        """Search decisions."""
        if query:
            return self.db.list_decisions(search=query, limit=limit)
        return self.db.list_decisions(limit=limit)
    
    def _search_blockers(self, 
                         query: Optional[str],
                         project: Optional[str],
                         limit: int) -> List[Blocker]:
        """Search blockers."""
        blockers = self.db.list_blockers(limit=limit * 2)
        
        if query:
            query_lower = query.lower()
            blockers = [b for b in blockers if 
                        query_lower in b.title.lower() or 
                        query_lower in (b.description or "").lower()]
        
        return blockers[:limit]
    
    def _apply_filters(self, 
                       results: Dict[str, List],
                       project: Optional[str],
                       from_date: Optional[str],
                       to: Optional[str],
                       tags: Optional[List[str]]) -> Dict[str, List]:
        """Apply common filters to results."""
        filtered = {}
        
        for key, items in results.items():
            filtered_items = items
            
            # Filter by project
            if project:
                filtered_items = [i for i in filtered_items 
                                  if hasattr(i, 'project_id') and i.project_id == project]
            
            # Filter by date
            if from_date or to:
                def in_date_range(item):
                    date_attr = None
                    if hasattr(item, 'created_at'):
                        date_attr = item.created_at
                    elif hasattr(item, 'date'):
                        date_attr = item.date
                    
                    if date_attr:
                        date_str = date_attr[:10] if len(date_attr) > 10 else date_attr
                        if from_date and date_str < from_date:
                            return False
                        if to and date_str > to:
                            return False
                    return True
                
                filtered_items = [i for i in filtered_items if in_date_range(i)]
            
            # Filter by tags
            if tags:
                filtered_items = [i for i in filtered_items 
                                  if hasattr(i, 'tags') and any(t in i.tags for t in tags)]
            
            filtered[key] = filtered_items
        
        return filtered
    
    def search_by_tag(self, tags: List[str], limit: int = 20) -> Dict[str, List[Any]]:
        """Search by tags only."""
        return self.search(
            query=None,
            type='all',
            tags=tags,
            limit=limit
        )
    
    def search_by_project(self, project_id: str, limit: int = 50) -> Dict[str, List[Any]]:
        """Get all items for a project."""
        return self.search(
            query=None,
            type='all',
            project=project_id,
            limit=limit
        )
    
    def print_results(self, results: Dict[str, List[Any]]) -> None:
        """Print search results to terminal."""
        total = sum(len(items) for items in results.values())
        
        if total == 0:
            print(f"\n{Colors.WARNING}No results found.{Colors.ENDC}")
            return
        
        print(f"\n{Colors.BOLD}Search Results ({total} found):{Colors.ENDC}\n")
        
        # Print entries
        if results['entries']:
            print(f"{Colors.CYAN}📄 Entries ({len(results['entries'])}):{Colors.ENDC}")
            for entry in results['entries']:
                print(f"  {Colors.BOLD}{entry.date}{Colors.ENDC}: {entry.summary.title}")
                if entry.summary.description:
                    print(f"    {truncate(entry.summary.description, 60)}")
            print()
        
        # Print tasks
        if results['tasks']:
            print(f"{Colors.GREEN}✓ Tasks ({len(results['tasks'])}):{Colors.ENDC}")
            for task in results['tasks']:
                status_color = Colors.GREEN if task.status == 'completed' else Colors.CYAN
                print(f"  [{status_color}{task.status[:3].upper()}{Colors.ENDC}] {task.title}")
            print()
        
        # Print decisions
        if results['decisions']:
            print(f"{Colors.BLUE}📋 Decisions ({len(results['decisions'])}):{Colors.ENDC}")
            for decision in results['decisions']:
                print(f"  {Colors.BOLD}{decision.id}{Colors.ENDC}: {decision.title}")
            print()
        
        # Print blockers
        if results['blockers']:
            print(f"{Colors.FAIL}🚧 Blockers ({len(results['blockers'])}):{Colors.ENDC}")
            for blocker in results['blockers']:
                esc_indicator = f" [L{blocker.escalation_level}]" if blocker.escalation_level > 0 else ""
                print(f"  {Colors.BOLD}{blocker.id}{Colors.ENDC}: {blocker.title}{esc_indicator}")
            print()
    
    def highlight_matches(self, text: str, query: str) -> str:
        """Highlight search matches in text."""
        if not query or not text:
            return text
        
        # Simple case-insensitive highlighting
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return pattern.sub(f"{Colors.WARNING}\\g<0>{Colors.ENDC}", text)


class QueryParser:
    """Parse advanced search queries."""
    
    @staticmethod
    def parse(query: str) -> Dict[str, Any]:
        """Parse query string into structured search parameters."""
        result = {
            'terms': [],
            'excluded': [],
            'project': None,
            'tag': None,
            'from_date': None,
            'to_date': None,
            'type': None
        }
        
        # Split query into parts
        parts = query.split()
        
        for part in parts:
            # Check for project filter
            if part.startswith('project:'):
                result['project'] = part[8:]
            
            # Check for tag filter
            elif part.startswith('tag:'):
                result['tag'] = part[4:]
            
            # Check for date filters
            elif part.startswith('from:'):
                result['from_date'] = part[5:]
            elif part.startswith('to:'):
                result['to_date'] = part[3:]
            
            # Check for type filter
            elif part.startswith('type:'):
                result['type'] = part[5:]
            
            # Check for exclusion
            elif part.startswith('-'):
                result['excluded'].append(part[1:])
            
            # Regular term
            elif part.startswith('+'):
                result['terms'].append(part[1:])
            else:
                result['terms'].append(part)
        
        return result
    
    @staticmethod
    def build_fts_query(parsed: Dict[str, Any]) -> str:
        """Build SQLite FTS query from parsed parameters."""
        parts = []
        
        # Include terms
        for term in parsed['terms']:
            parts.append(term)
        
        # Exclude terms
        for term in parsed['excluded']:
            parts.append(f"NOT {term}")
        
        return " AND ".join(parts) if parts else "*"
