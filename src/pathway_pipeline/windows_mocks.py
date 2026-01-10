"""
Mocks for Pathway components to support running on Windows (where Pathway is not available).
"""

class MockTable:
    """Mock for pw.Table that supports chaining."""
    def __init__(self, data=None):
        self.data = data or []

    def select(self, *args, **kwargs):
        # In a real shim, we might try to execute the logic.
        # For now, just return self to allow chaining without crashing.
        print("    ⚠️  (Mock) .select() called - data transformation logic skipped in Windows mode")
        return self

    def flatten(self, *args, **kwargs):
        print("    ⚠️  (Mock) .flatten() called")
        return self
        
    def __iter__(self):
        return iter(self.data)
        
    def __getitem__(self, item):
        return self

class MockUDF:
    """Mock for pw.UDF base class."""
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        pass

class MockExpression:
    """Mock for pw.this and pw.io expressions."""
    def __getattr__(self, name):
        return self
    def __call__(self, *args, **kwargs):
        return self
    def __getitem__(self, item):
        return self

def mock_apply(func, *args):
    """Mock for pw.apply."""
    return None

class MockSchema:
    """Mock for pw.Schema."""
    pass
