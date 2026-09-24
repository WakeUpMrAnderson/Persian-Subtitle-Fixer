"""Tests for subtitle_processor."""

from subtitle_processor import is_persian_arabic_text


def test_is_persian_arabic_text_with_persian():
    """Should return True for text containing Persian characters."""
    assert is_persian_arabic_text("سلام دنیا") is True


def test_is_persian_arabic_text_with_english():
    """Should return False for plain English text."""
    assert is_persian_arabic_text("Hello World") is False


def test_is_persian_arabic_text_with_mixed():
    """Should return True when enough Persian characters are present."""
    assert is_persian_arabic_text("Hello سلام World دنیا") is True
