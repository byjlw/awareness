import argparse
import json
from project_rank_tracker import ProjectRankTracker
from search_terms import SearchTermsLoader

def main():
    parser = argparse.ArgumentParser(description='Google Search Project Ranking Tracker')
    parser.add_argument('--key', required=True, help='Google Custom Search API key')
    parser.add_argument('--cx', required=True, help='Google Custom Search Engine ID')
    parser.add_argument('--projects', required=True, nargs='+', help='Projects to track in search results')
    parser.add_argument('--num-results', type=int, default=10, help='Number of results to check for each search (max 10)')
    parser.add_argument('--usage', action='store_true', help='Show API usage and exit')
    
    # Search term arguments
    term_group = parser.add_mutually_exclusive_group()
    term_group.add_argument('-t', '--terms', nargs='+', help='Space-separated search terms')
    term_group.add_argument('-f', '--file', help='File with search terms (one per line)')
    
    # Output option
    parser.add_argument('-o', '--output', help='Save results to JSON file')
    
    args = parser.parse_args()
    
    tracker = ProjectRankTracker(args.key, args.cx, args.projects)
    
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
            terms = SearchTermsLoader.load_terms(args.file)
        except Exception as e:
            print(f"Error loading terms: {str(e)}")
            return
    else:
        terms = args.terms
    
    # Perform search
    results = tracker.search_project_ranks(terms, num_results=args.num_results)
    
    # Save results if output file specified
    if results and args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()