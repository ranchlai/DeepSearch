import json
import os

import requests


def search(query: str, gl: str = "cn"):

    url = "https://google.serper.dev/search"

    payload = json.dumps({"q": query, "gl": gl})
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    text = ""
    for i, item in enumerate(data["organic"]):
        text += (
            f"[Source {i}] {item.get('title', '')}\n"
            + item.get("snippet", "")
            + "\n"
            + item.get("link", "")
            + "\n"
        )
        text += "---\n"
    return text
