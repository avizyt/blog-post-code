from src.query_engine.query_processor import query_codebase

def test_query_codebase():
    response = query_codebase("What does the main function do?")
    assert response is not None
