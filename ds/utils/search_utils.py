import json
import os

import requests


def search_google(query: str, gl: str = "cn"):

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


def search_jina_ai(query: str):

    url = f"https://s.jina.ai/?q={query}"
    headers = {
        "Authorization": os.getenv("JINA_AI_API_KEY"),
        "X-Respond-With": "no-content",
    }

    response = requests.get(url, headers=headers)

    return response.text


def search(query: str):
    if os.getenv("JINA_AI_API_KEY"):
        return search_jina_ai(query)
    else:
        return search_google(query)


if __name__ == "__main__":
    print(search("Jina AI"))
