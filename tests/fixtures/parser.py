import pytest

from dot_analyzer.dot_parser import DotParser


@pytest.fixture
def parser():
    return DotParser()
