import os
import json
import pytest
from awareness.charts.generate_charts import (
    load_json_files,
    generate_search_count_chart,
    generate_ranking_charts,
    format_number
)

@pytest.fixture
def sample_data_dir(tmp_path):
    # Create a temporary directory for test data
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    
    # Create sample search results JSON
    search_data = {
        "python programming": {
            "count": 1500000,
            "timestamp": "2024-02-26 10:30:45"
        },
        "python tutorial": {
            "count": 800000,
            "timestamp": "2024-02-26 10:30:47"
        }
    }
    
    with open(data_dir / "search_results.json", "w") as f:
        json.dump(search_data, f)
    
    # Create sample project rankings JSON
    ranking_data = {
        "python web framework": {
            "total_results": 1234567,
            "project_rankings": {
                "Django": 1,
                "Flask": 3,
                "FastAPI": 5
            },
            "timestamp": "2024-02-26 10:30:45"
        }
    }
    
    with open(data_dir / "project_rankings.json", "w") as f:
        json.dump(ranking_data, f)
    
    return data_dir

@pytest.fixture
def output_dir(tmp_path):
    # Create a temporary directory for output charts
    charts_dir = tmp_path / "charts"
    charts_dir.mkdir()
    return charts_dir

def test_format_number():
    assert format_number(1234) == "1.2 thousand"
    assert format_number(1234567) == "1.2 million"
    assert format_number(123) == "123"
    assert format_number(0) == "0"

def test_load_json_files(sample_data_dir):
    data = load_json_files(str(sample_data_dir))
    
    assert len(data) == 2
    assert "search_results.json" in data
    assert "project_rankings.json" in data
    
    # Verify search results content
    search_data = data["search_results.json"]
    assert "python programming" in search_data
    assert search_data["python programming"]["count"] == 1500000
    
    # Verify ranking content
    ranking_data = data["project_rankings.json"]
    assert "python web framework" in ranking_data
    assert ranking_data["python web framework"]["project_rankings"]["Django"] == 1

def test_generate_search_count_chart(sample_data_dir, output_dir):
    data = load_json_files(str(sample_data_dir))
    generate_search_count_chart(data, str(output_dir))
    
    # Check if chart file was created
    expected_file = output_dir / "search_counts_search_results.png"
    assert expected_file.exists()
    
    # Add a test case for log scale
    search_data = {
        "term1": {
            "count": 1000000,
            "timestamp": "2024-02-26 10:30:45"
        },
        "term2": {
            "count": 100,
            "timestamp": "2024-02-26 10:30:47"
        }
    }
    
    # Create a new file with data that should trigger log scale
    with open(sample_data_dir / "log_scale_test.json", "w") as f:
        json.dump(search_data, f)
    
    data = load_json_files(str(sample_data_dir))
    generate_search_count_chart(data, str(output_dir))
    
    # Check if log scale chart was created
    expected_log_file = output_dir / "search_counts_log_scale_test.png"
    assert expected_log_file.exists()

def test_generate_ranking_charts(sample_data_dir, output_dir):
    data = load_json_files(str(sample_data_dir))
    generate_ranking_charts(data, str(output_dir))
    
    # Check if chart file was created
    expected_file = output_dir / "rankings_python web framework_project_rankings.png"
    assert expected_file.exists()
    
    # Test with missing rankings
    ranking_data = {
        "test term": {
            "total_results": 1000000,
            "project_rankings": {
                "Project1": 1,
                "Project2": None,
                "Project3": 50
            },
            "timestamp": "2024-02-26 10:30:45"
        }
    }
    
    # Create a new file with rankings including None values
    with open(sample_data_dir / "test_rankings.json", "w") as f:
        json.dump(ranking_data, f)
    
    data = load_json_files(str(sample_data_dir))
    generate_ranking_charts(data, str(output_dir))
    
    # Check if chart with missing rankings was created
    expected_missing_file = output_dir / "rankings_test term_test_rankings.png"
    assert expected_missing_file.exists()

def test_api_usage_json_ignored(sample_data_dir):
    # Create an api_usage.json file that should be ignored
    api_usage = {
        "date": "2024-02-26",
        "count": 50
    }
    with open(sample_data_dir / "api_usage.json", "w") as f:
        json.dump(api_usage, f)
    
    data = load_json_files(str(sample_data_dir))
    assert "api_usage.json" not in data