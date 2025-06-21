import pytest

from dot_parser import DotParser


@pytest.fixture
def parser():
    return DotParser()
