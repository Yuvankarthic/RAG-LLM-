import streamlit as st
from pathlib import Path
import requests

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# -----------------------------
# App config
# -----------------------------
st.set_page_config(page_title="PIM / MDM AI Assistant")
st.title("PIM / MDM AI Assistant")

# -----------------------------
# Load knowledge base
# -----------------------------
BASE_DIR = Path(__file__).parent
KB_DIR = BASE_DIR / "knowledge_base"

files = [
    "pim_basics.md",
    "mdm_basics.md",
    "attributes.md",
    "data_quality.md",
]

documents = []
for f in files:
    p = KB_DIR / f
    if p.exists():
        documents.append(p.read_text(encoding="utf-8"))

# -----------------------------
# Build embeddings
# -----------------------------
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embeddings = embedder.encode(documents, convert_to_numpy=True)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# -----------------------------
# Ollama call
# -----------------------------
def ask_ollama(context, question):
    prompt = f"""
You are a PIM and MDM domain assistant.

You must answer ONLY questions related to:
- Product Information Management (PIM)
- Master Data Management (MDM)
- Product attributes
- Data quality and governance

If the question is outside this scope, politely say you can only help with PIM/MDM topics.

Context:
{context}

Question:
{question}

Answer clearly and in business-friendly language.
"""

    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral:latest",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    return r.json()["response"]

# -----------------------------
# UI
# -----------------------------
question = st.text_input("Ask a PIM / MDM question")

if question:
    q_emb = embedder.encode([question], convert_to_numpy=True)
    _, idx = index.search(q_emb, k=2)
    context = "\n\n".join([documents[i] for i in idx[0]])

    with st.spinner("Thinking..."):
        answer = ask_ollama(context, question)

    st.markdown("### Answer")
    st.write(answer)
