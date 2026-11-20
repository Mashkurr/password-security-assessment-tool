from unittest.mock import Mock, patch

from core.breach import check_breach


@patch("core.breach.requests.get")
def test_breach_match(mock_get):
    response = Mock()
    response.raise_for_status.return_value = None
    response.text = "D09CA3762AF61E59520943DC26494F8941B:42\n00000000000000000000000000000000000:1"
    mock_get.return_value = response
    result = check_breach("123456")
    assert result["status"] == "Found"
    assert result["count"] == 42


@patch("core.breach.requests.get")
def test_breach_not_found(mock_get):
    response = Mock()
    response.raise_for_status.return_value = None
    response.text = "00000000000000000000000000000000000:1"
    mock_get.return_value = response
    assert check_breach("an-unlisted-demonstration-value")["status"] == "Not Found"


@patch("core.breach.requests.get")
def test_invalid_service_response_is_not_reported_as_not_found(mock_get):
    response = Mock()
    response.raise_for_status.return_value = None
    response.text = "malformed-response"
    mock_get.return_value = response
    assert check_breach("test")["status"] == "Check Unavailable"


@patch("core.breach.requests.get", side_effect=Exception("network disabled"))
def test_unexpected_errors_are_not_silently_misreported(mock_get):
    try:
        check_breach("test")
    except Exception as error:
        assert str(error) == "network disabled"
