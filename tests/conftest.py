import pytest


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("DISCORD_BRIDGE_URL", "https://discord.com/api/webhooks/test")
    monkeypatch.setenv("DISCORD_BRIDGE_PORT", "5000")

    import discord_keel_bridge

    discord_keel_bridge.app.config["TESTING"] = True
    with discord_keel_bridge.app.test_client() as test_client:
        yield test_client
