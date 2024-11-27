import pytest
import json
from unittest.mock import patch, MagicMock
from awareness.core.search_tracker import GoogleSearchTracker

@pytest.fixture
def tracker():
    return GoogleSearchTracker('test_key', 'test_cx')

@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        'searchInformation': {
            'totalResults': '1234567'
        }
    }
    return mock

def test_load_daily_usage_new_file(tracker, tmp_path):
    tracker.usage_file = str(tmp_path / 'api_usage.json')
    usage = tracker._load_daily_usage()
    assert usage['count'] == 0
    assert 'date' in usage

def test_load_daily_usage_existing_file(tracker, tmp_path):
    usage_file = tmp_path / 'api_usage.json'
    test_usage = {'date': '2024-01-01', 'count': 50}
    with open(usage_file, 'w') as f:
        json.dump(test_usage, f)
    
    tracker.usage_file = str(usage_file)
    usage = tracker._load_daily_usage()
    assert usage['count'] == 0  # Should reset since date is old
    assert usage['date'] != '2024-01-01'

def test_save_daily_usage(tracker, tmp_path):
    tracker.usage_file = str(tmp_path / 'api_usage.json')
    tracker.daily_usage = {'date': '2024-01-01', 'count': 75}
    tracker._save_daily_usage()
    
    with open(tracker.usage_file) as f:
        saved_usage = json.load(f)
    assert saved_usage == tracker.daily_usage

def test_get_remaining_calls(tracker):
    tracker.daily_usage = {'date': '2024-01-01', 'count': 75}
    remaining = tracker.get_remaining_calls()
    assert remaining['used_today'] == 75
    assert remaining['free_remaining'] == 25
    assert remaining['date'] == '2024-01-01'

@patch('requests.get')
def test_search_single_term(mock_get, tracker, mock_response):
    mock_get.return_value = mock_response
    results = tracker.search(['test term'])
    
    assert 'test term' in results
    assert results['test term']['count'] == 1234567
    assert 'timestamp' in results['test term']
    mock_get.assert_called_once()

@patch('requests.get')
def test_search_multiple_terms(mock_get, tracker, mock_response):
    mock_get.return_value = mock_response
    results = tracker.search(['term1', 'term2'])
    
    assert len(results) == 2
    assert 'term1' in results
    assert 'term2' in results
    assert mock_get.call_count == 2

@patch('requests.get')
def test_search_error_handling(mock_get, tracker):
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "API quota exceeded"
    mock_get.return_value = mock_response
    
    results = tracker.search(['test term'])
    assert results == {}

def test_search_daily_limit_check(tracker):
    tracker.daily_usage['count'] = 10000
    with pytest.raises(Exception) as exc_info:
        tracker.search(['test term'])
    assert "Would exceed daily limit" in str(exc_info.value)

@patch('builtins.input', return_value='n')
def test_search_cost_warning_no(mock_input, tracker):
    tracker.daily_usage['count'] = 95
    results = tracker.search(['term1', 'term2', 'term3', 'term4', 'term5', 'term6'])
    assert results is None

@patch('builtins.input', return_value='y')
@patch('requests.get')
def test_search_cost_warning_yes(mock_get, mock_input, tracker, mock_response):
    mock_get.return_value = mock_response
    tracker.daily_usage['count'] = 95
    results = tracker.search(['term1', 'term2', 'term3', 'term4', 'term5', 'term6'])
    assert results is not None
    assert mock_get.call_count == 6