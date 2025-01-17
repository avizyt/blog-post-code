from src.indexer.code_parser import parse_codebase


def test_parse_codebase():
    structure = parse_codebase("test_data/")
    assert len(structure) > 0
