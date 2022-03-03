# Mangle path so we can run the import
import sys

sys.path.append("plugins")

from template_vars import adjust_header_hierarchy
import pytest


@pytest.mark.parametrize(
    "html,max,expected",
    (
        # This should be left alone
        ("<h3>h3</h3><h4>h4</h4>", 3, "<h3>h3</h3><h4>h4</h4>"),
        # These should be updated
        ("<h1>h1</h1><h2>h2</h2>", 3, "<h3>h1</h3><h4>h2</h4>"),
        ("<h1>h1</h1><h2>h2</h2>", 2, "<h2>h1</h2><h3>h2</h3>"),
        # Should not go higher than h6
        ("<h1>h1</h1><h2>h2</h2><h3>h3</h3>", 5, "<h5>h1</h5><h6>h2</h6><h6>h3</h6>"),
    ),
)
def test_adjust_header_hierarchy(html, max, expected):
    actual = adjust_header_hierarchy(html, max)
    assert actual == expected
