import time
import requests

URL = "http://localhost:11434/api/generate"
PROMPT = """Write a concise but useful overview of how to build a local AI assistant for a developer workstation. Cover these points:
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
    "prompt": PROMPT,
    "stream": False,
    "options": {
        "num_ctx": 2048,
    },
}

request_count = 0
success_count = 0
failure_count = 0
latencies = []

for i in range(3):
    request_count += 1
    start = time.time()
    try:
        response = requests.post(URL, json=payload, timeout=180)
        response.raise_for_status()
        response.json()
        success_count += 1
        status = "success"
    except Exception as exc:
        failure_count += 1
        status = f"failure: {exc}"

    elapsed = time.time() - start
    latencies.append(elapsed)
    print(f"Request {request_count}: {status}")
    print(f"Elapsed time: {elapsed:.2f}s")
    print()

avg_latency = sum(latencies) / len(latencies) if latencies else 0
print("Summary:")
print(f"Request count: {request_count}")
print(f"Success count: {success_count}")
print(f"Failure count: {failure_count}")
print(f"Average latency: {avg_latency:.2f}s")
