from pathlib import Path


def test_twilio_mcp_seed_present_once():
    script_path = Path(__file__).parent / "scripts" / "initialize_mcp_integrations.py"
    content = script_path.read_text(encoding="utf-8")
    assert content.count('"name": "Twilio MCP Server"') == 1
    assert "@twilio-alpha/mcp" in content
    assert "{account_sid}/{api_key}:{api_secret}" in content

