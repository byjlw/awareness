#!/usr/bin/env python3
import argparse
import sys
import json
import os

# Add the parent directory to the Python path to allow running from any directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from awareness.core.search_tracker import GoogleSearchTracker
from awareness.core.project_rank_tracker import ProjectRankTracker
from awareness.charts.generate_charts import main as generate_charts

def search_command(args):
    """Handle search-related commands"""
    tracker = GoogleSearchTracker(args.key, args.cx)
    
    if args.usage:
        usage = tracker.get_remaining_calls()
        print(f"\nAPI Usage for {usage['date']}:")
        print(f"Queries used today: {usage['used_today']}")
        print(f"Free queries remaining: {usage['free_remaining']}")
        if usage['used_today'] >= 100:
            print("You are now in the paid tier ($0.005 per query)")
        return

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

def rank_command(args):
    """Handle project ranking commands"""
    tracker = ProjectRankTracker(args.key, args.cx, args.projects)
    
    if args.usage:
        usage = tracker.get_remaining_calls()
        print(f"\nAPI Usage for {usage['date']}:")
        print(f"Queries used today: {usage['used_today']}")
        print(f"Free queries remaining: {usage['free_remaining']}")
        if usage['used_today'] >= 100:
            print("You are now in the paid tier ($0.005 per query)")
        return

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

    # Perform ranking search
    results = tracker.search_project_ranks(terms, args.num_results)
    
    # Save results if output file specified
    if results and args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"\nResults saved to {args.output}")

def charts_command(args):
    """Handle chart generation commands"""
    sys.argv = [sys.argv[0]] + ['--input-dir', args.input_dir, '--output-dir', args.output_dir]
    generate_charts()

def main():
    parser = argparse.ArgumentParser(
        description='Project Awareness Toolkit - Track and analyze open source project visibility'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Track search result counts')
    search_parser.add_argument('--key', required=True, help='Google Custom Search API key')
    search_parser.add_argument('--cx', required=True, help='Google Custom Search Engine ID')
    search_parser.add_argument('--usage', action='store_true', help='Show API usage and exit')
    term_group = search_parser.add_mutually_exclusive_group()
    term_group.add_argument('-t', '--terms', nargs='+', help='Space-separated search terms')
    term_group.add_argument('-f', '--file', help='File with search terms (one per line)')
    search_parser.add_argument('-o', '--output', help='Save results to JSON file')
    
    # Rank command
    rank_parser = subparsers.add_parser('rank', help='Track project rankings in search results')
    rank_parser.add_argument('--key', required=True, help='Google Custom Search API key')
    rank_parser.add_argument('--cx', required=True, help='Google Custom Search Engine ID')
    rank_parser.add_argument('--usage', action='store_true', help='Show API usage and exit')
    rank_parser.add_argument('--projects', nargs='+', required=True, help='Projects to track')
    term_group = rank_parser.add_mutually_exclusive_group()
    term_group.add_argument('-t', '--terms', nargs='+', help='Space-separated search terms')
    term_group.add_argument('-f', '--file', help='File with search terms (one per line)')
    rank_parser.add_argument('--num-results', type=int, default=100,
                          help='Number of results to check (default: 100)')
    rank_parser.add_argument('-o', '--output', help='Save results to JSON file')
    
    # Charts command
    charts_parser = subparsers.add_parser('charts', help='Generate charts from JSON results')
    charts_parser.add_argument('--input-dir', default='output',
                           help='Directory containing JSON files (default: output)')
    charts_parser.add_argument('--output-dir', default='charts',
                           help='Directory to save charts (default: charts)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute the appropriate command
    if args.command == 'search':
        search_command(args)
    elif args.command == 'rank':
        rank_command(args)
    elif args.command == 'charts':
        charts_command(args)

if __name__ == '__main__':
    main()