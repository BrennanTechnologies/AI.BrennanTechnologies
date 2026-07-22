import requests

url = "http://localhost:11434/api/generate"
prompt = """You are an expert systems architect and senior software engineer. Analyze the following complex scenario in depth and produce a comprehensive, structured response.

Context:
You are designing a large-scale AI platform for a global enterprise with 200,000 employees, multiple cloud regions, strict compliance requirements, and real-time inference workloads. The platform must support:
- multi-model orchestration
- low-latency inference
- secure data handling
- observability and cost control
- disaster recovery
- multilingual support
- integration with Microsoft 365, Azure, and internal enterprise systems

Task:
1. Break down the architecture into layers: ingestion, model serving, orchestration, security, observability, storage, and networking.
2. For each layer, describe the key components, responsibilities, and tradeoffs.
3. Compare at least three deployment options:
   - single-region deployment
   - multi-region active-active
   - hybrid cloud with on-prem inference
4. For each option, discuss:
   - latency
   - cost
   - resilience
   - compliance posture
   - operational complexity
5. Recommend the best architecture for the enterprise and justify it.
6. Provide a sample reference implementation plan for 90 days.
7. Include a table of risks, mitigations, and owners.
8. End with a concise executive summary and a list of next steps.

Requirements:
- Be highly detailed.
- Use precise technical language.
- Include real-world examples and practical engineering considerations.
- Avoid generic advice.
- Produce a long, nuanced response with strong reasoning and structured formatting.
"""

payload = {
    "model": "llama3.1",
    "prompt": prompt,
    "stream": False,
    "options": {
        "num_ctx": 4096,
    },
}

response = requests.post(url, json=payload, timeout=300)
response.raise_for_status()
data = response.json()
print(data.get("response", ""))
