
from stocks.main import compare_values

def test_compare_values():
    assert compare_values(3, '>', 2) == True
    assert compare_values(2, '<', 3) == True

