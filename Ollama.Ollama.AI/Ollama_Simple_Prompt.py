# Example: curl http://localhost:11434/api/generate -d "{\"model\":\"llama3.1\",\"prompt\":\"Hello\"}"

import requests

url = "http://localhost:11434/api/generate"
payload = {"model": "llama3.1", "prompt": "Say hello in one sentence", "stream": False}

try:
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    print(data.get("response", ""))
except requests.exceptions.RequestException as exc:
    print(f"Request failed: {exc}")
    raise
