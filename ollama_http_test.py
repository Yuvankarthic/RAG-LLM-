import requests

print("Sending request to Ollama...")

r = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "mistral:latest",
        "prompt": "Say hello in one sentence.",
        "stream": False
    },
    timeout=60
)

print("Status code:", r.status_code)
print("Response:", r.json()["response"])
