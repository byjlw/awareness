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

def format_number(num):
    """Format large numbers into human-readable strings."""
    if num >= 1_000_000:
        return f'{num/1_000_000:.1f} million'
    elif num >= 1_000:
        return f'{num/1_000:.1f} thousand'
    return str(num)

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
            
            # Create bar plot
            ax = plt.gca()
            bars = plt.bar(terms, counts)
            
            # Determine if we should use log scale
            count_range = max(counts) / (min(counts) if min(counts) > 0 else 1)
            if count_range > 100:  # Use log scale if range is more than 2 orders of magnitude
                ax.set_yscale('log')
            
            # Add value labels on top of each bar
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       format_number(height),
                       ha='center', va='bottom', rotation=0)
            
            plt.title(f'Search Results Count - {filename}')
            plt.xticks(rotation=45, ha='right')
            plt.ylabel('Number of Results (log scale)' if ax.get_yscale() == 'log' else 'Number of Results')
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
                total_results = info.get('total_results', 0)
                
                plt.figure(figsize=(10, 6))
                ax = plt.gca()
                bars = plt.bar(projects, ranks)
                
                # Add value labels on top of each bar
                for bar in bars:
                    height = bar.get_height()
                    label = 'Not found' if height == 100 else f'#{int(height)}'
                    # Position the text inside the bar for better visibility
                    ax.text(bar.get_x() + bar.get_width()/2., height - 5,
                           label,
                           ha='center', va='top', rotation=0,
                           color='white', fontweight='bold')
                
                plt.title(f'Project Rankings for "{term}"\n(Total Results: {format_number(total_results)})')
                plt.xticks(rotation=45, ha='right')
                plt.ylabel('Rank Position')
                plt.ylim(0, 105)  # Give some space for the labels
                plt.gca().invert_yaxis()  # Invert Y-axis so better ranks are higher
                
                # Add grid for better readability
                plt.grid(axis='y', linestyle='--', alpha=0.3)
                
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