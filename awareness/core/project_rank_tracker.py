# project_rank_tracker.py
from typing import List, Dict, Optional
from datetime import datetime, date
import requests
import json
import time
from awareness.core.search_tracker import GoogleSearchTracker

class ProjectRankTracker(GoogleSearchTracker):
    def __init__(self, api_key: str, search_engine_id: str, projects: List[str]):
        super().__init__(api_key, search_engine_id)
        self.projects = projects

    def _get_search_results(self, term: str, num_results: int = 100) -> Dict:
        """Get detailed search results for a term with pagination"""
        url = "https://www.googleapis.com/customsearch/v1"
        all_items = []
        total_results = 0
        
        pages_needed = (num_results + 9) // 10
        pages_needed = min(pages_needed, 10)
        
        for page in range(pages_needed):
            start_index = (page * 10) + 1
            
            # Calculate remaining items needed
            remaining = num_results - len(all_items)
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': term,
                'num': min(10, remaining),  # Request only what we need
                'start': start_index
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                break
                
            data = response.json()
            if 'items' in data:
                all_items.extend(data['items'])
                if total_results == 0 and 'searchInformation' in data:
                    total_results = int(data['searchInformation']['totalResults'])
            
            # Check if we found all projects or reached the requested number
            temp_data = {'items': all_items}
            project_ranks = self._find_project_ranks(temp_data)
            if all(rank is not None for rank in project_ranks.values()) or len(all_items) >= num_results:
                break
                
            time.sleep(1)
        
        # Create a new dictionary with limited results
        return {
            'items': all_items[:num_results],  # Slice before returning
            'searchInformation': {
                'totalResults': str(total_results)
            }
        }

    def _find_project_ranks(self, search_data: Dict) -> Dict[str, Optional[int]]:
        """Find the ranking position of each project in search results"""
        project_ranks = {project: None for project in self.projects}
        
        if 'items' not in search_data:
            return project_ranks

        for idx, item in enumerate(search_data['items']):
            content = (
                item.get('title', '') + ' ' + 
                item.get('snippet', '') + ' ' +
                item.get('link', '')
            ).lower()
            
            for project in self.projects:
                if project.lower() in content and project_ranks[project] is None:
                    # Calculate actual rank based on item's position
                    actual_rank = idx + 1
                    project_ranks[project] = actual_rank
                    
        return project_ranks

    def search_project_ranks(self, terms: List[str], num_results: int = 100, show_progress: bool = True) -> Dict:
        """Search for terms and track project rankings"""
        results = {}
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_queries = len(terms) * 10  # Maximum possible API calls
        remaining_free = max(0, 100 - self.daily_usage['count'])
        
        if total_queries > remaining_free:
            paid_queries = total_queries - remaining_free
            print(f"\nWarning: Maximum possible API queries: {total_queries}")
            print(f"Free queries remaining today: {remaining_free}")
            print(f"Maximum potential cost: ${paid_queries * 0.005:.2f}")
            # Skip confirmation in test mode
            if show_progress and input("Continue? (y/n): ").lower() != 'y':
                return None

        for term in terms:
            try:
                search_data = self._get_search_results(term, num_results)
                project_ranks = self._find_project_ranks(search_data)
                total_results = int(search_data['searchInformation']['totalResults'])

                results[term] = {
                    'total_results': total_results,
                    'project_rankings': project_ranks,
                    'timestamp': timestamp
                }

                pages_fetched = (len(search_data['items']) + 9) // 10
                self.daily_usage['count'] += pages_fetched
                self._save_daily_usage()

                if show_progress:
                    print(f"\n{term}")
                    print(f"Total results: {total_results:,}")
                    for project, rank in project_ranks.items():
                        rank_str = f"Rank #{rank}" if rank else "Not found in first 100 results"
                        print(f"{project}: {rank_str}")
                    print("-" * 40)

            except Exception as e:
                print(f"Error processing '{term}': {str(e)}")

        return results