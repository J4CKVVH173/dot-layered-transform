import pytest

from dot_analyzer.core.dot_parser import DotParser


@pytest.fixture
def parser():
    return DotParser()
