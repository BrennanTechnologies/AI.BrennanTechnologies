# curl http://localhost:11434/api/generate -d "{\"model\":\"llama3.1\",\"prompt\":\"Hello\"}"

import requests

resp = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3.1", "prompt": "Say hello in one sentence"}
)

print(resp.json()["response"])