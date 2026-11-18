#!/usr/bin/env python3
import json
import os

import requests
from flask import Flask, jsonify, request
from gevent.pywsgi import WSGIServer

app = Flask(__name__)


def _discord_url() -> str:
    return os.environ["DISCORD_BRIDGE_URL"]


def _port() -> int:
    return int(os.environ["DISCORD_BRIDGE_PORT"])


@app.route("/v1/incoming", methods=["POST"])
def incoming():
    original = request.json
    # Build a Discord embed from the incoming Keel payload.
    # Keel payloads vary – use whatever fields are present.
    title = original.get("name") or "Keel notification"
    description = original.get("message") or ""
    timestamp = original.get("createdAt") or original.get("timestamp")
    embed = {
        "title": title,
        "description": description,
        "timestamp": timestamp,
        "color": 3447003,  # Discord "blurple" color
    }
    discord = {"embeds": [embed]}
    result = requests.post(
        _discord_url(),
        data=json.dumps(discord),
        headers={"Content-Type": "application/json"},
    )
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        resp = jsonify(success=False)
        resp.status_code = result.status_code
    else:
        print(f"Payload delivered successfully, code {result.status_code}.")
        resp = jsonify(success=True)
        resp.status_code = 200
    return resp


if __name__ == "__main__":
    http_server = WSGIServer(("0.0.0.0", _port()), app)
    print(f"Bridge listening on port: {_port()}")
    http_server.serve_forever()