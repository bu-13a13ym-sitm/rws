import json
from urllib.request import Request, urlopen

def post_discord(message: str, webhook_url: str):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (private use) Python-urllib/3.10",
    }
    data = {"content": message}
    request = Request(
        webhook_url,
        data=json.dumps(data).encode(),
        headers=headers,
    )

    with urlopen(request) as res:
        assert res.getcode() == 204

if __name__ == "__main__":
    webhook_url = "https://canary.discord.com/api/webhooks/1375120983576547438/i9MsyTZI_uuqhmHSazPk7T3bqPMZgCanCffFzfN7k3gP7HG7VQV2fT-n8BuyO_qZZ6pK"
    post_discord('Webhook test', webhook_url)