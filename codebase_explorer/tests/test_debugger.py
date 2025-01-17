from src.debugger.stack_analyzer import analyze_stack_trace

def test_analyze_stack_trace():
    trace = 'File "example.py", line 10, in <module>'
    result = analyze_stack_trace(trace)
    assert "example.py" in result
