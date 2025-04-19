import codecs
import json
import os

import requests


def decode_escaped_utf8(text):
    # First decode the Python string literal escape sequences
    decoded_bytes = codecs.escape_decode(text.encode("utf-8"))[0]

    # Then decode as UTF-8
    return decoded_bytes.decode("utf-8", errors="replace")


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
        "Accept": "application/json",
        "X-Return-Format": "markdown",
    }

    response = requests.get(url, headers=headers)
    result = response.json()
    text = ""
    for item in result["data"]:
        # title', 'url', 'description', 'date', 'content'
        text += f"{item.get('title', '')}\n{item.get('description', '')}\n{item.get('url', '')}\n{item.get('date', '')}\n---\n"
    return text


def search(query: str):
    if os.getenv("JINA_AI_API_KEY"):
        return search_jina_ai(query)
    else:
        return search_google(query)


if __name__ == "__main__":
    print(search("Jina AI"))
