# Project Awareness

A toolkit for analyzing and tracking the visibility and awareness of open source projects across various platforms and metrics. Currently supports Google search result analysis with plans to expand to other awareness indicators.

## Features

### Basic Search Results Tracking
- Track search result counts for multiple terms
- Support for command-line terms or input from various file formats
- Usage tracking for Google Custom Search API quota
- Cost estimation for paid tier queries
- Optional JSON output of results
- Built-in rate limiting to comply with API requirements

### Project Ranking Tracking
- Track where specific projects appear in search results (up to first 100 results)
- Monitor multiple projects across different search terms
- Early exit optimization - stops searching once all projects are found
- Detailed output including total result counts for each term
- Supports multiple input file formats (txt, csv, json, yaml)
- Detailed JSON output with rankings and total results

## Prerequisites

1. Google Custom Search API Key
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Custom Search API
   - Create credentials (API key)

2. Custom Search Engine ID
   - Visit [Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Create a new search engine
   - Set it to search the entire web
   - Get the Search Engine ID (cx)

3. Python Requirements
```bash
pip install requests pyyaml
```

## Usage

### Command Line Interface

The toolkit provides a unified command-line interface with three main commands: `search`, `rank`, and `charts`.

#### Basic Search Results Counter

Search for specific terms:
```bash
awareness search --key YOUR_API_KEY --cx YOUR_SEARCH_ENGINE_ID -t "term1" "term2" "term3"
```

Search using terms from a file:
```bash
awareness search --key YOUR_API_KEY --cx YOUR_SEARCH_ENGINE_ID -f terms.txt
```

Save results to a JSON file:
```bash
awareness search --key YOUR_API_KEY --cx YOUR_SEARCH_ENGINE_ID -t "term1" "term2" -o results.json
```

#### Project Ranking Tracker

Track project rankings for specific terms:
```bash
awareness rank --key YOUR_API_KEY --cx YOUR_SEARCH_ENGINE_ID \
    --projects "project1" "project2" \
    -t "search term1" "search term2" \
    -o rankings.json
```

Track project rankings using terms from a file:
```bash
awareness rank --key YOUR_API_KEY --cx YOUR_SEARCH_ENGINE_ID \
    --projects "project1" "project2" \
    -f terms.json \
    --num-results 100 \
    -o rankings.json
```

#### Generate Charts

Generate charts from JSON results in the default directories:
```bash
awareness charts
```

Generate charts with custom directories:
```bash
awareness charts --input-dir path/to/json/files --output-dir path/to/charts
```

#### Check API Usage

View remaining free queries and usage status:
```bash
awareness search --key YOUR_API_KEY --cx YOUR_SEARCH_ENGINE_ID --usage
# or
awareness rank --key YOUR_API_KEY --cx YOUR_SEARCH_ENGINE_ID --usage
```

## Input File Formats

The toolkit supports multiple file formats for search terms:

### Text File (terms.txt)
```text
term1
term2
term3
```

### CSV File (terms.csv)
```csv
term1
term2
term3
```

### JSON File (terms.json)
```json
{
    "terms": [
        "term1",
        "term2",
        "term3"
    ]
}
```
or
```json
[
    "term1",
    "term2",
    "term3"
]
```

### YAML File (terms.yml)
```yaml
terms:
  - term1
  - term2
  - term3
```
or
```yaml
- term1
- term2
- term3
```

## Output Formats

### Basic Search Results
```json
{
    "term1": {
        "count": 1234567,
        "timestamp": "2024-11-26 10:30:45"
    },
    "term2": {
        "count": 7654321,
        "timestamp": "2024-11-26 10:30:47"
    }
}
```

### Project Rankings
Command line output:
```
search term1
Total results: 1,234,567
project1: Rank #15
project2: Not found in first 100 results
----------------------------------------
```

JSON output:
```json
{
    "search term1": {
        "total_results": 1234567,
        "project_rankings": {
            "project1": 15,
            "project2": null
        },
        "timestamp": "2024-11-26 10:30:45"
    }
}
```
Note: `null` indicates the project was not found in the searched results.

## API Usage and Costs

- Free tier: 100 queries per day
- Paid tier: $5 per 1,000 queries ($0.005 per query)
- Daily limit: 10,000 queries
- Each page of 10 results counts as one API query
- Project ranking searches use multiple queries per term (up to 10)
- Early exit optimization reduces API usage by stopping once projects are found
- The script will warn you before exceeding the free tier and show estimated costs

## Files Created

- `api_usage.json`: Tracks daily API usage
- Output JSON file (if specified with `-o/--output`)
- Charts directory (when using generate_charts.py)

## Generating Charts

The toolkit includes a script to generate visual charts from the JSON output files. To use it, you'll need additional Python packages:

```bash
pip install matplotlib
```

### Usage

Generate charts from JSON files in the default output directory:
```bash
python generate_charts.py
```

Specify custom input and output directories:
```bash
python generate_charts.py --input-dir path/to/json/files --output-dir path/to/charts
```

### Generated Charts

The script generates two types of charts:

1. Search Results Count Charts
   - Bar charts showing the number of results for each search term
   - One chart per JSON file containing basic search results

2. Project Ranking Charts
   - Bar charts showing the ranking position of each project
   - One chart per search term in each JSON file containing project rankings
   - Lower rank numbers (higher bars) indicate better visibility

## Error Handling

The toolkit handles common errors including:
- Invalid API credentials
- File not found or invalid format
- API quota exceeded
- Network issues
- Invalid search terms
- Pagination errors

## Notes

- The script includes a 1-second delay between queries to comply with API best practices
- Result counts are approximate (as provided by Google)
- Usage tracking resets daily
- API key and Search Engine ID are required for all operations
- Project ranking searches analyze title, snippet, and URL of each result
- Maximum of 100 results can be checked per term
- Early exit feature saves API calls by stopping once all projects are found

## Running Tests

The project uses pytest for testing. To run the tests:

1. Install the package in development mode with test dependencies:
```bash
pip install -e ".[dev]"
```

Alternatively, you can install just the test dependencies if you don't want to install the package:
```bash
pip install -r requirements-dev.txt
```

2. Run the tests:
```bash
pytest
```

This will run all tests in the `tests` directory and display the results with verbose output. The test suite includes:
- Unit tests for chart generation functionality
- Verification of JSON file loading
- Chart output validation
- API usage file handling

The tests are automatically run on GitHub Actions for Python versions 3.7 through 3.12 whenever code is pushed to the main branch or a pull request is created.

