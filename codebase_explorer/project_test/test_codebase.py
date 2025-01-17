# test_codebase.py
from query_engine.query_processor import QueryProcessor


def test_query():
    processor = QueryProcessor()
    # Intentionally cause an error by not initializing properly
    result = processor.query("test")
    print(result)


if __name__ == "__main__":
    try:
        test_query()
    except Exception as e:
        import traceback

        with open("codebase_error.txt", "w") as f:
            f.write(traceback.format_exc())
        print(f"Error occurred: {e}")
