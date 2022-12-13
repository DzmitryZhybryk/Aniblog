from unittest.mock import MagicMock

import pytest


def count_occurrences(cursor, cust_id):
    cursor.execute("SELECT count(id) FROM users WHERE customer_id = %s", (cust_id))
    total_count = cursor.fetchone()[0]
    if total_count == 0:
        return True
    else:
        return False


@pytest.mark.parametrize("count,expected",
                         [(0, True), (1, False), (25, False), (None, False)]
                         )
def test_count_occurences(count, expected):
    mock_cursor = MagicMock()
    mock_cursor.configure_mock(
        **{
            "fetchone.return_value": [count]
        }
    )

    actual = count_occurrences(mock_cursor, "some_id")
    assert actual == expected
