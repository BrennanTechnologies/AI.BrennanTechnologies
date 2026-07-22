import requests

url = "http://localhost:11434/api/generate"
prompt = """Write a concise but useful overview of how to build a local AI assistant for a developer workstation. Cover these points:
- what the assistant should do well
- which model size is appropriate
- how to run it locally with Ollama
- how to connect it to a Python script
- what privacy and security considerations matter
- what tradeoffs exist between speed and quality

Keep the response structured, practical, and about 400-600 words long.
"""

payload = {
    "model": "llama3.1",
    "prompt": prompt,
    "stream": False,
    "options": {
        "num_ctx": 2048,
    },
}

response = requests.post(url, json=payload, timeout=180)
response.raise_for_status()
data = response.json()
print(data.get("response", ""))
