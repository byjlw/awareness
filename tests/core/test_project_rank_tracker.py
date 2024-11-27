import pytest
from unittest.mock import patch, MagicMock
from awareness.core.project_rank_tracker import ProjectRankTracker

@pytest.fixture
def tracker():
    return ProjectRankTracker('test_key', 'test_cx', ['project1', 'project2'])

@pytest.fixture
def mock_search_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        'items': [
            {
                'title': 'Project1 - Best Framework',
                'snippet': 'Description of project1',
                'link': 'https://project1.com'
            },
            {
                'title': 'Some Other Result',
                'snippet': 'Random content',
                'link': 'https://example.com'
            },
            {
                'title': 'Project2 Documentation',
                'snippet': 'Learn about project2',
                'link': 'https://project2.com'
            }
        ],
        'searchInformation': {
            'totalResults': '12345'
        }
    }
    return mock

def test_find_project_ranks_no_items(tracker):
    search_data = {}
    rankings = tracker._find_project_ranks(search_data)
    assert rankings == {'project1': None, 'project2': None}

def test_find_project_ranks_with_matches(tracker):
    search_data = {
        'items': [
            {
                'title': 'Project1 Homepage',
                'snippet': 'About project1',
                'link': 'https://project1.com'
            },
            {
                'title': 'Random Result',
                'snippet': 'Not relevant',
                'link': 'https://example.com'
            },
            {
                'title': 'Project2 Docs',
                'snippet': 'Documentation for project2',
                'link': 'https://project2.com'
            }
        ]
    }
    rankings = tracker._find_project_ranks(search_data)
    assert rankings['project1'] == 1
    assert rankings['project2'] == 3

def test_find_project_ranks_partial_matches(tracker):
    search_data = {
        'items': [
            {
                'title': 'Project1 Homepage',
                'snippet': 'About project1',
                'link': 'https://project1.com'
            },
            {
                'title': 'Random Result',
                'snippet': 'Not relevant',
                'link': 'https://example.com'
            }
        ]
    }
    rankings = tracker._find_project_ranks(search_data)
    assert rankings['project1'] == 1
    assert rankings['project2'] is None

@patch('requests.get')
def test_get_search_results(mock_get, tracker, mock_search_response):
    mock_get.return_value = mock_search_response
    results = tracker._get_search_results('test term')
    
    assert 'items' in results
    assert 'searchInformation' in results
    assert len(results['items']) == 3
    assert results['searchInformation']['totalResults'] == '12345'

@patch('requests.get')
def test_get_search_results_pagination(mock_get, tracker, mock_search_response):
    # Set up mock to return different items for each page
    mock_search_response.json.side_effect = [
        {'items': [{'title': f'Result {i}'} for i in range(1, 11)], 'searchInformation': {'totalResults': '100'}},
        {'items': [{'title': f'Result {i}'} for i in range(11, 21)], 'searchInformation': {'totalResults': '100'}},
        {'items': [{'title': f'Result {i}'} for i in range(21, 26)], 'searchInformation': {'totalResults': '100'}}
    ]
    mock_get.return_value = mock_search_response
    
    results = tracker._get_search_results('test term', num_results=25)
    
    # Should make 3 API calls (25 results = 3 pages of 10)
    assert mock_get.call_count == 3
    assert len(results['items']) == 25

@patch('requests.get')
def test_get_search_results_error(mock_get, tracker):
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_get.return_value = mock_response
    
    results = tracker._get_search_results('test term')
    assert results == {'items': [], 'searchInformation': {'totalResults': '0'}}

@patch('builtins.input', return_value='n')
def test_search_project_ranks_cost_warning_no(mock_input, tracker):
    tracker.daily_usage['count'] = 90
    results = tracker.search_project_ranks(['term1', 'term2'])
    assert results is None

@patch('builtins.input', return_value='y')
@patch('requests.get')
def test_search_project_ranks_cost_warning_yes(mock_get, mock_input, tracker, mock_search_response):
    mock_get.return_value = mock_search_response
    tracker.daily_usage['count'] = 90
    results = tracker.search_project_ranks(['term1', 'term2'])
    
    assert results is not None
    assert 'term1' in results
    assert 'term2' in results
    for term_data in results.values():
        assert 'total_results' in term_data
        assert 'project_rankings' in term_data
        assert 'timestamp' in term_data

@patch('builtins.input', return_value='y')
@patch('requests.get')
def test_early_exit_optimization(mock_get, mock_input, tracker, mock_search_response):
    # Modify mock response so all projects are found on first page
    mock_search_response.json.return_value['items'] = [
        {
            'title': 'Project1 First',
            'snippet': 'About project1',
            'link': 'https://project1.com'
        },
        {
            'title': 'Project2 Second',
            'snippet': 'About project2',
            'link': 'https://project2.com'
        }
    ]
    mock_get.return_value = mock_search_response
    
    # Request 50 results, but should exit after first page since all projects are found
    results = tracker.search_project_ranks(['test term'], num_results=50)
    assert mock_get.call_count == 1  # Only one API call needed