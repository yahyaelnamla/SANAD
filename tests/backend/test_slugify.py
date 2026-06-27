"""Tests for opinion comparison utilities."""


from backend.app.utils.slugify import slugify


def test_slugify_basic():
    assert slugify("AAOIFI Shariah Board") == "aaoifi-shariah-board"


def test_slugify_strips_special_chars():
    assert slugify("Sheikh Yusuf al-Qaradawi") == "sheikh-yusuf-al-qaradawi"
