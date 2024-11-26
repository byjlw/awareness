import requests
import json
import argparse
from datetime import datetime, date
import time
from typing import Dict

class GoogleSearchTracker:
    def __init__(self, api_key, search_engine_id):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.usage_file = 'api_usage.json'
        self.daily_usage = self._load_daily_usage()
    
    def _load_daily_usage(self):
        try:
            with open(self.usage_file, 'r') as f:
                usage = json.load(f)
                # Reset if it's a new day
                if usage['date'] != date.today().isoformat():
                    return {'date': date.today().isoformat(), 'count': 0}
                return usage
        except (FileNotFoundError, json.JSONDecodeError):
            return {'date': date.today().isoformat(), 'count': 0}
    
    def _save_daily_usage(self):
        with open(self.usage_file, 'w') as f:
            json.dump(self.daily_usage, f)
    
    def get_remaining_calls(self):
        """Get remaining free API calls for today"""
        used = self.daily_usage['count']
        free_remaining = max(0, 100 - used)
        return {
            'used_today': used,
            'free_remaining': free_remaining,
            'date': self.daily_usage['date']
        }
    
    def search(self, terms, show_progress=True):
        """Search for terms and return their result counts"""
        url = "https://www.googleapis.com/customsearch/v1"
        results = {}
        
        # Check if we'll exceed daily limit
        if self.daily_usage['count'] + len(terms) > 10000:
            raise Exception("Error: Would exceed daily limit of 10,000 queries")
        
        # Check free tier and warn about costs
        remaining_free = max(0, 100 - self.daily_usage['count'])
        if len(terms) > remaining_free:
            paid_queries = len(terms) - remaining_free
            print(f"Warning: {len(terms)} queries will exceed free tier (100 queries per day)")
            print(f"You have {remaining_free} free queries remaining today")
            print(f"Estimated cost: ${paid_queries * 0.005:.2f}")
            if input("Continue? (y/n): ").lower() != 'y':
                return None
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for term in terms:
            try:
                params = {
                    'key': self.api_key,
                    'cx': self.search_engine_id,
                    'q': term,
                    'num': 1
                }
                
                response = requests.get(url, params=params)
                
                if response.status_code != 200:
                    print(f"Error searching for '{term}': {response.text}")
                    continue
                
                data = response.json()
                count = int(data['searchInformation']['totalResults'])
                
                results[term] = {
                    'count': count,
                    'timestamp': timestamp
                }
                
                # Update usage count
                self.daily_usage['count'] += 1
                self._save_daily_usage()
                
                if show_progress:
                    print(f"Term: {term}")
                    print(f"Results: {count:,}")
                    print("-" * 40)
                
                time.sleep(1)  # Be nice to the API
                
            except Exception as e:
                print(f"Error processing term '{term}': {str(e)}")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Google Custom Search API Results Tracker')
    parser.add_argument('--key', required=True, help='Google Custom Search API key')
    parser.add_argument('--cx', required=True, help='Google Custom Search Engine ID')
    parser.add_argument('--usage', action='store_true', help='Show API usage and exit')
    
    # Search term arguments
    term_group = parser.add_mutually_exclusive_group()
    term_group.add_argument('-t', '--terms', nargs='+', help='Space-separated search terms')
    term_group.add_argument('-f', '--file', help='File with search terms (one per line)')
    
    # Output option
    parser.add_argument('-o', '--output', help='Save results to JSON file')
    
    args = parser.parse_args()
    
    tracker = GoogleSearchTracker(args.key, args.cx)
    
    # Just show usage if flag is present
    if args.usage:
        usage = tracker.get_remaining_calls()
        print(f"\nAPI Usage for {usage['date']}:")
        print(f"Queries used today: {usage['used_today']}")
        print(f"Free queries remaining: {usage['free_remaining']}")
        if usage['used_today'] >= 100:
            print("You are now in the paid tier ($0.005 per query)")
        return
    
    # Handle search terms
    if not (args.terms or args.file):
        parser.error("Either -t/--terms or -f/--file is required unless --usage is specified")
    
    # Get terms
    if args.file:
        try:
            with open(args.file) as f:
                terms = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            return
    else:
        terms = args.terms
    
    # Perform search
    results = tracker.search(terms)
    
    # Save results if output file specified
    if results and args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()