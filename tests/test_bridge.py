import json as json_lib
from unittest.mock import ANY, MagicMock, patch

import requests


def test_incoming_returns_error(client, monkeypatch):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
    mock_response.status_code = 400

    with patch("discord_keel_bridge.requests.post", return_value=mock_response) as mock_post:
        response = client.post(
            "/v1/incoming",
            json={"name": "Test User", "message": "Error Test", "createdAt": "2024-01-01T00:00:00Z"},
        )

    assert response.status_code == 400
    assert response.get_json() == {"success": False}
    mock_post.assert_called_once()
    payload = json_lib.loads(mock_post.call_args.kwargs["data"])
    assert payload["embeds"][0]["title"] == "Test User"
    assert payload["embeds"][0]["description"] == "Error Test"
    assert payload["embeds"][0]["timestamp"] == "2024-01-01T00:00:00Z"
    assert isinstance(payload["embeds"][0]["color"], int)

def test_incoming_returns_success(client):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 204

    with patch("discord_keel_bridge.requests.post", return_value=mock_response) as mock_post:
        response = client.post(
            "/v1/incoming",
            json={"name": "Test User", "message": "Hello", "createdAt": "2024-01-01T00:00:00Z"},
        )

    assert response.status_code == 200
    assert response.get_json() == {"success": True}
    mock_post.assert_called_once()
    payload = json_lib.loads(mock_post.call_args.kwargs["data"])
    assert "content" not in payload
    assert len(payload["embeds"]) == 1
    assert payload["embeds"][0]["title"] == "Test User"
    assert payload["embeds"][0]["description"] == "Hello"
    assert payload["embeds"][0]["timestamp"] == "2024-01-01T00:00:00Z"
    assert "color" in payload["embeds"][0]
    assert "fields" not in payload["embeds"][0]


def test_incoming_missing_name_falls_back(client):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 204

    with patch("discord_keel_bridge.requests.post", return_value=mock_response) as mock_post:
        response = client.post(
            "/v1/incoming",
            json={"message": "no name here", "createdAt": "2024-01-01T00:00:00Z"},
        )

    assert response.status_code == 200
    payload = json_lib.loads(mock_post.call_args.kwargs["data"])
    assert payload["embeds"][0]["title"] == "Keel notification"
    assert payload["embeds"][0]["description"] == "no name here"
