#!/usr/bin/env python3
import json
import glob
import os
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

def load_json_files(directory):
    """Load all JSON files from the specified directory."""
    json_files = glob.glob(os.path.join(directory, '*.json'))
    data = {}
    for file_path in json_files:
        if file_path.endswith('api_usage.json'):
            continue
        with open(file_path, 'r') as f:
            data[os.path.basename(file_path)] = json.load(f)
    return data

def generate_search_count_chart(data, output_dir):
    """Generate line charts for search result counts over time."""
    for filename, results in data.items():
        terms = []
        counts = []
        timestamps = []
        
        for term, info in results.items():
            if 'count' in info:  # Basic search results
                terms.append(term)
                counts.append(info['count'])
                timestamps.append(datetime.strptime(info['timestamp'], "%Y-%m-%d %H:%M:%S"))
        
        if terms:  # Basic search results
            plt.figure(figsize=(12, 6))
            plt.bar(terms, counts)
            plt.title(f'Search Results Count - {filename}')
            plt.xticks(rotation=45, ha='right')
            plt.ylabel('Number of Results')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'search_counts_{os.path.splitext(filename)[0]}.png'))
            plt.close()

def generate_ranking_charts(data, output_dir):
    """Generate charts for project rankings."""
    for filename, results in data.items():
        for term, info in results.items():
            if 'project_rankings' in info:  # Project rankings
                rankings = info['project_rankings']
                projects = list(rankings.keys())
                ranks = [rankings[p] if rankings[p] is not None else 100 for p in projects]
                
                plt.figure(figsize=(10, 6))
                plt.bar(projects, ranks)
                plt.title(f'Project Rankings for "{term}" - {filename}')
                plt.xticks(rotation=45, ha='right')
                plt.ylabel('Rank (lower is better)')
                plt.ylim(0, 100)
                plt.gca().invert_yaxis()  # Invert Y-axis so better ranks are higher
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, f'rankings_{term}_{os.path.splitext(filename)[0]}.png'))
                plt.close()

def main():
    parser = argparse.ArgumentParser(description='Generate charts from search results JSON files')
    parser.add_argument('--input-dir', default='output', help='Directory containing JSON files (default: output)')
    parser.add_argument('--output-dir', default='charts', help='Directory to save charts (default: charts)')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load JSON data
    data = load_json_files(args.input_dir)
    
    # Generate charts
    generate_search_count_chart(data, args.output_dir)
    generate_ranking_charts(data, args.output_dir)
    
    print(f"Charts have been generated in the '{args.output_dir}' directory.")

if __name__ == "__main__":
    main()