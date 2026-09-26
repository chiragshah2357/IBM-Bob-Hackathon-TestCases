import pytest

from taskboard.pagination import Page, validate_page_args


def make_page(page: int = 1, page_size: int = 20, total: int = 0) -> Page:
    return Page(items=[], page=page, page_size=page_size, total=total)


@pytest.mark.parametrize(
    ("total", "page_size", "expected"),
    [
        (0, 20, 0),
        (1, 20, 1),
        (20, 20, 1),
        (21, 20, 2),
        (45, 20, 3),
        (40, 20, 2),
        (3, 1, 3),
        (100, 100, 1),
    ],
)
def test_total_pages_rounds_up(total, page_size, expected):
    assert make_page(page_size=page_size, total=total).total_pages == expected


def test_has_next_true_before_last_page():
    assert make_page(page=1, page_size=20, total=45).has_next is True
    assert make_page(page=2, page_size=20, total=45).has_next is True


def test_has_next_false_on_last_page():
    assert make_page(page=3, page_size=20, total=45).has_next is False


def test_has_next_false_on_exact_multiple_last_page():
    assert make_page(page=2, page_size=20, total=40).has_next is False


def test_has_next_false_past_the_end():
    assert make_page(page=7, page_size=20, total=45).has_next is False


def test_has_next_false_for_empty_listing():
    assert make_page(page=1, page_size=20, total=0).has_next is False


def test_page_rejects_negative_total():
    with pytest.raises(ValueError):
        make_page(total=-1)


def test_page_rejects_invalid_page_number():
    with pytest.raises(ValueError):
        make_page(page=0)


@pytest.mark.parametrize(("page", "page_size"), [(1, 1), (1, 100), (50, 20)])
def test_validate_page_args_accepts_valid_values(page, page_size):
    validate_page_args(page, page_size)


@pytest.mark.parametrize("page", [0, -1])
def test_validate_page_args_rejects_page_below_one(page):
    with pytest.raises(ValueError):
        validate_page_args(page, 20)


@pytest.mark.parametrize("page_size", [0, -5])
def test_validate_page_args_rejects_page_size_below_one(page_size):
    with pytest.raises(ValueError):
        validate_page_args(1, page_size)


@pytest.mark.parametrize("value", ["1", 1.0, None, True])
def test_validate_page_args_rejects_non_integers(value):
    with pytest.raises(ValueError):
        validate_page_args(value, 20)
    with pytest.raises(ValueError):
        validate_page_args(1, value)
