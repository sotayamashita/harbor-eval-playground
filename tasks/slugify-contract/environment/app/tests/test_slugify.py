from slugify import slugify


# space -> hyphen
def test_convert_spaces_to_hyphen():
    assert slugify("Hello World") == "hello-world"


# underscore -> separator
def test_treats_underscores_as_separators():
    assert slugify("  A__B  ") == "a-b"


# non-ascii removal
def test_removes_non_ascii_characters():
    assert slugify("日本語 Test") == "test"


# repeated hyphen collapse
def test_collapses_repeated_hyphens():
    assert slugify("foo---bar") == "foo-bar"
