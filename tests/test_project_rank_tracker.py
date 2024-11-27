import pytest
from unittest.mock import Mock, patch
from awareness.core.project_rank_tracker import ProjectRankTracker

def create_mock_response(items, total_results="100"):
    return {
        'items': items,
        'searchInformation': {
            'totalResults': total_results
        }
    }

def create_mock_item(title, snippet="", link=""):
    return {
        'title': title,
        'snippet': snippet,
        'link': link
    }

def test_respects_num_results():
    tracker = ProjectRankTracker("fake_key", "fake_engine", ["project1"])
    
    # Create 100 mock items
    mock_items = [create_mock_item(f"Result {i}") for i in range(100)]
    
    with patch.object(tracker, '_get_search_results') as mock_search:
        # Test with 50 results
        tracker.search_project_ranks(["test term"], num_results=50, show_progress=False)
        
        # Verify _get_search_results was called with num_results=50
        mock_search.assert_called_with("test term", 50)

def test_correct_rank_first_page():
    tracker = ProjectRankTracker("fake_key", "fake_engine", ["target_project"])
    
    # Create mock items where target is at position 5
    mock_items = [
        create_mock_item("Result 1"),
        create_mock_item("Result 2"),
        create_mock_item("Result 3"),
        create_mock_item("Result 4"),
        create_mock_item("target_project found here"),  # Position 5
        create_mock_item("Result 6"),
    ]
    
    with patch.object(tracker, '_get_search_results') as mock_search:
        mock_search.return_value = create_mock_response(mock_items)
        results = tracker.search_project_ranks(["test term"], show_progress=False)
        
        assert results["test term"]["project_rankings"]["target_project"] == 5

def test_correct_rank_second_page():
    tracker = ProjectRankTracker("fake_key", "fake_engine", ["target_project"])
    
    # Create mock items where target is at position 15 (second page)
    mock_items = [create_mock_item(f"Result {i}") for i in range(14)]
    mock_items.append(create_mock_item("target_project found here"))  # Position 15
    
    with patch.object(tracker, '_get_search_results') as mock_search:
        mock_search.return_value = create_mock_response(mock_items)
        results = tracker.search_project_ranks(["test term"], show_progress=False)
        
        assert results["test term"]["project_rankings"]["target_project"] == 15

def test_limits_results_exactly():
    tracker = ProjectRankTracker("fake_key", "fake_engine", ["project1"])
    
    # Create more items than requested
    mock_items = [create_mock_item(f"Result {i}") for i in range(60)]
    mock_response = create_mock_response(mock_items)
    
    with patch.object(tracker, '_get_search_results') as mock_search:
        # Set up the mock to return our items
        mock_search.return_value = mock_response
        
        # Request exactly 50 results through the search_project_ranks method
        results = tracker.search_project_ranks(["test term"], num_results=50, show_progress=False)
        
        # Verify that _get_search_results was called with num_results=50
        mock_search.assert_called_with("test term", 50)
        
        # Verify the mock was called exactly once
        assert mock_search.call_count == 1

def test_multiple_projects_different_pages():
    tracker = ProjectRankTracker("fake_key", "fake_engine", ["project1", "project2"])
    
    # Create items where projects are on different pages
    mock_items = [create_mock_item(f"Result {i}") for i in range(25)]
    mock_items[4] = create_mock_item("project1 found here")  # Position 5
    mock_items[14] = create_mock_item("project2 found here")  # Position 15
    
    with patch.object(tracker, '_get_search_results') as mock_search:
        mock_search.return_value = create_mock_response(mock_items)
        results = tracker.search_project_ranks(["test term"], show_progress=False)
        
        assert results["test term"]["project_rankings"]["project1"] == 5
        assert results["test term"]["project_rankings"]["project2"] == 15