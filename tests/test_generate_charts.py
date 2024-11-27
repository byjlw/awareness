import os
import sys
import json
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate_charts import load_json_files, generate_search_count_chart, generate_ranking_charts

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

def test_generate_ranking_charts(sample_data_dir, output_dir):
    data = load_json_files(str(sample_data_dir))
    generate_ranking_charts(data, str(output_dir))
    
    # Check if chart file was created
    expected_file = output_dir / "rankings_python web framework_project_rankings.png"
    assert expected_file.exists()

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