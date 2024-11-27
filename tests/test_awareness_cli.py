import pytest
import json
import os
from unittest.mock import patch, MagicMock
from awareness.awareness_cli import search_command, rank_command, charts_command

@pytest.fixture
def mock_args():
    return MagicMock(
        key='test_key',
        cx='test_cx',
        terms=['test term'],
        file=None,
        output=None,
        usage=False,
        projects=['project1', 'project2'],
        num_results=100,
        input_dir='input',
        output_dir='output'
    )

@pytest.fixture
def mock_search_results():
    return {
        'test term': {
            'count': 12345,
            'timestamp': '2024-01-01 12:00:00'
        }
    }

@pytest.fixture
def mock_rank_results():
    return {
        'test term': {
            'total_results': 12345,
            'project_rankings': {
                'project1': 1,
                'project2': 5
            },
            'timestamp': '2024-01-01 12:00:00'
        }
    }

@patch('awareness.awareness_cli.GoogleSearchTracker')
def test_search_command_basic(MockSearchTracker, mock_args, mock_search_results):
    mock_tracker = MagicMock()
    mock_tracker.search.return_value = mock_search_results
    MockSearchTracker.return_value = mock_tracker
    
    search_command(mock_args)
    
    MockSearchTracker.assert_called_once_with('test_key', 'test_cx')
    mock_tracker.search.assert_called_once_with(['test term'])

@patch('awareness.awareness_cli.GoogleSearchTracker')
def test_search_command_with_output(MockSearchTracker, mock_args, mock_search_results, tmp_path):
    output_file = tmp_path / 'results.json'
    mock_args.output = str(output_file)
    
    mock_tracker = MagicMock()
    mock_tracker.search.return_value = mock_search_results
    MockSearchTracker.return_value = mock_tracker
    
    search_command(mock_args)
    
    assert output_file.exists()
    with open(output_file) as f:
        saved_results = json.load(f)
    assert saved_results == mock_search_results

@patch('awareness.awareness_cli.GoogleSearchTracker')
def test_search_command_with_file(MockSearchTracker, mock_args, tmp_path):
    terms_file = tmp_path / 'terms.txt'
    with open(terms_file, 'w') as f:
        f.write('term1\nterm2\nterm3')
    mock_args.terms = None
    mock_args.file = str(terms_file)
    
    mock_tracker = MagicMock()
    MockSearchTracker.return_value = mock_tracker
    
    search_command(mock_args)
    
    mock_tracker.search.assert_called_once_with(['term1', 'term2', 'term3'])

@patch('awareness.awareness_cli.ProjectRankTracker')
def test_rank_command_basic(MockRankTracker, mock_args, mock_rank_results):
    mock_tracker = MagicMock()
    mock_tracker.search_project_ranks.return_value = mock_rank_results
    MockRankTracker.return_value = mock_tracker
    
    rank_command(mock_args)
    
    MockRankTracker.assert_called_once_with('test_key', 'test_cx', ['project1', 'project2'])
    mock_tracker.search_project_ranks.assert_called_once_with(['test term'], 100)

@patch('awareness.awareness_cli.ProjectRankTracker')
def test_rank_command_with_output(MockRankTracker, mock_args, mock_rank_results, tmp_path):
    output_file = tmp_path / 'rankings.json'
    mock_args.output = str(output_file)
    
    mock_tracker = MagicMock()
    mock_tracker.search_project_ranks.return_value = mock_rank_results
    MockRankTracker.return_value = mock_tracker
    
    rank_command(mock_args)
    
    assert output_file.exists()
    with open(output_file) as f:
        saved_results = json.load(f)
    assert saved_results == mock_rank_results

@patch('awareness.awareness_cli.generate_charts')
def test_charts_command(mock_generate_charts, mock_args):
    charts_command(mock_args)
    mock_generate_charts.assert_called_once()

def test_search_command_usage(mock_args):
    mock_args.usage = True
    mock_args.terms = None
    
    with patch('awareness.awareness_cli.GoogleSearchTracker') as MockSearchTracker:
        mock_tracker = MagicMock()
        mock_tracker.get_remaining_calls.return_value = {
            'date': '2024-01-01',
            'used_today': 50,
            'free_remaining': 50
        }
        MockSearchTracker.return_value = mock_tracker
        
        search_command(mock_args)
        
        mock_tracker.get_remaining_calls.assert_called_once()
        mock_tracker.search.assert_not_called()

def test_rank_command_usage(mock_args):
    mock_args.usage = True
    mock_args.terms = None
    
    with patch('awareness.awareness_cli.ProjectRankTracker') as MockRankTracker:
        mock_tracker = MagicMock()
        mock_tracker.get_remaining_calls.return_value = {
            'date': '2024-01-01',
            'used_today': 50,
            'free_remaining': 50
        }
        MockRankTracker.return_value = mock_tracker
        
        rank_command(mock_args)
        
        mock_tracker.get_remaining_calls.assert_called_once()
        mock_tracker.search_project_ranks.assert_not_called()