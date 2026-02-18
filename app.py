import streamlit as st
import requests
import json
from pathlib import Path
import re
import pandas as pd # New import for data handling

# --- Dependency Imports ---
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ======================================================================================
# 1. APP CONFIGURATION & STYLING
# ======================================================================================

st.set_page_config(
    page_title="PIM / MDM AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    body {font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif; background-color: #f8f9fa;}
    .stApp {background-color: #f8f9fa;}
    [data-testid="stVerticalBlock"] .st-emotion-cache-12w0qpk {background-color: #ffffff; border: 1px solid #e1e4e8; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ======================================================================================
# 2. SESSION STATE INITIALIZATION
# ======================================================================================

# New: Initialize session state for holding uploaded data and analysis
if 'data_analysis_summary' not in st.session_state:
    st.session_state.data_analysis_summary = None
if 'user_dataframe' not in st.session_state:
    st.session_state.user_dataframe = None
if 'uploaded_filename' not in st.session_state:
    st.session_state.uploaded_filename = None

# ======================================================================================
# 3. RESOURCE LOADING & DATA ANALYSIS
# ======================================================================================

BASE_DIR = Path(__file__).parent
KB_DIR = BASE_DIR / "knowledge_base"
PDF_DIR = KB_DIR / "pdfs"

@st.cache_resource
def load_ai_resources():
    # This function remains as before, loading general knowledge base content
    all_docs_as_text = []
    md_files_to_load = ["pim_basics.md", "mdm_basics.md", "attributes.md", "data_quality.md"]
    for file_name in md_files_to_load:
        file_path = KB_DIR / file_name
        if file_path.exists(): all_docs_as_text.append(file_path.read_text(encoding="utf-8"))
        else: st.warning(f"Knowledge base file not found: {file_name}")

    if not PDF_DIR.exists(): PDF_DIR.mkdir()
    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if pdf_files:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        for pdf_path in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_path))
                pages = loader.load_and_split(text_splitter=text_splitter)
                for page in pages: all_docs_as_text.append(page.page_content)
            except Exception as e: st.warning(f"Could not process PDF {pdf_path.name}: {e}")

    if not all_docs_as_text:
        st.error("Knowledge base is empty.")
        return None, None, None
    try:
        embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        embeddings = embedder.encode(all_docs_as_text, convert_to_numpy=True)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return embedder, index, all_docs_as_text
    except Exception as e:
        st.error(f"Failed to initialize AI resources: {e}")
        return None, None, None

embedder, index, documents = load_ai_resources()

# --- New: Data Analysis Function ---
def perform_pim_analysis(df: pd.DataFrame) -> str:
    """Performs a PIM-specific analysis of the user's dataframe and returns a summary string."""
    summary = []
    
    # Identify key columns, case-insensitive
    cols = {c.lower(): c for c in df.columns}
    sku_col = cols.get('sku')
    name_col = cols.get('product_name', cols.get('name'))

    # 1. Check for mandatory attributes
    missing_mandatory = []
    if not sku_col: missing_mandatory.append("SKU (or 'sku')")
    if not name_col: missing_mandatory.append("Product Name (or 'name')")
    
    if missing_mandatory:
        summary.append(f"**Critical Issue:** Mandatory columns are missing: {', '.join(missing_mandatory)}. Without these, products cannot be identified.")
    
    # 2. Completeness Check
    missing_values = df.isnull().sum()
    missing_attributes = missing_values[missing_values > 0]
    if not missing_attributes.empty:
        summary.append("\n**Completeness Issues Found:**")
        for col, count in missing_attributes.items():
            summary.append(f"- The attribute '{col}' is missing in **{count}** of **{len(df)}** products.")
    
    # 3. Uniqueness Check (if SKU exists)
    duplicates = 0
    if sku_col:
        duplicates = df[sku_col].duplicated().sum()
        if duplicates > 0:
            summary.append(f"\n**Uniqueness Issue:** Found **{duplicates}** duplicate SKUs. Each product must have a unique SKU.")

    # 4. PIM Readiness Verdict
    readiness = "High"
    if len(missing_mandatory) > 0 or duplicates > 0:
        readiness = "Low"
    elif not missing_attributes.empty:
        readiness = "Medium"
        
    summary.insert(0, f"### PIM Readiness: {readiness}\n")
    return "\n".join(summary)


# ======================================================================================
# 4. CORE AI & PERSONA LOGIC
# ======================================================================================

def get_relevant_context(query: str) -> str:
    # This function is unchanged
    if not embedder or not index: return "Error: AI resources are not available."
    query_embedding = embedder.encode([query], convert_to_numpy=True)
    _, top_indices = index.search(query_embedding, k=3)
    return "\n\n---\n\n".join([documents[i] for i in top_indices[0]])

def ask_llm(prompt: str) -> str:
    """General purpose function to query the Ollama LLM."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral:latest", "prompt": prompt, "stream": False},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("response", "No response from model.").strip()
    except requests.exceptions.Timeout:
        return "Error: The request to the AI model timed out."
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to the local AI model. Details: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Modified: The core orchestrator function ---
def get_assistant_response(user_query: str) -> str:
    """
    Generates the assistant's response, deciding which logic to use:
    1. Simple Greeting: For "hi", "hello", etc.
    2. Data-Aware Analysis: If a file has been uploaded.
    3. General RAG: If no file is present.
    """
    normalized_query = re.sub(r'[^\w\s]', '', user_query).lower().strip()
    if normalized_query in ["hi", "hello", "hey"]: return "Hi! 👋 How can I help you with PIM or MDM today?"
    if normalized_query in ["thanks", "thank you"]: return "You're welcome! Let me know if you have other questions."

    # Data-Aware Path
    if st.session_state.data_analysis_summary:
        with st.spinner("Analyzing your data with PIM knowledge..."):
            rag_context = get_relevant_context(user_query)
            
            # New prompt that combines data analysis with general knowledge
            prompt = f"""
You are a PIM/MDM AI Assistant helping a user analyze their product data.

You have two sources of information:
1. A pre-generated "Data Analysis Summary" of the user's uploaded file.
2. A "Knowledge Base Context" with general PIM/MDM concepts.

Your task is to synthesize these two sources to answer the user's question.

RULES:
- Base your answer ONLY on the provided data analysis and knowledge base context.
- Use the "Knowledge Base Context" to explain WHY a finding from the summary is important.
- If the user asks a general question like "What's wrong with my data?", summarize the key findings from the "Data Analysis Summary" and explain the risks using the knowledge base.
- If the user asks a specific question (e.g., "Which attributes are missing?"), answer it directly from the summary.
- Follow the required output format: Use headings like "What I Found", "Why It Matters", and "What to Check Next". Be professional and clear.
- If the answer isn't in the provided information, state that clearly. Do not make things up.

---
DATA ANALYSIS SUMMARY (from user's file: {st.session_state.uploaded_filename}):
{st.session_state.data_analysis_summary}
---
KNOWLEDGE BASE CONTEXT:
{rag_context}
---

Based on all the above, answer the following user query.

User Query: "{user_query}"
"""
            return ask_llm(prompt)
    
    # General RAG Path (no file uploaded)
    else:
        # If user asks about their data without uploading a file
        if any(word in user_query.lower() for word in ['my data', 'my file', 'my sheet']):
            return "Please upload a product data file (CSV or Excel) first, and I'll be happy to help you analyze it."
            
        with st.spinner("Searching the knowledge base..."):
            rag_context = get_relevant_context(user_query)
            prompt = f"""
You are a professional, human-like PIM / MDM AI Assistant. Your behavior rules are strict.
1. DOMAIN RESTRICTION: Answer ONLY PIM/MDM questions.
2. CONTEXT USAGE: Answer ONLY using the context. If the answer is not in the context, say: "This information is not available in the current PIM/MDM knowledge base."
3. COMMUNICATION STYLE: Be natural and professional.
---
CONTEXT:
{rag_context}
---
Based only on the context and rules, answer the query: "{user_query}"
"""
            return ask_llm(prompt)

# ======================================================================================
# 5. STREAMLIT UI LAYOUT
# ======================================================================================

st.title("🤖 PIM / MDM AI Assistant")
st.markdown("Your expert on PIM/MDM. Ask questions about our knowledge base, or upload your product data for analysis.")
st.divider()

# --- New: File Upload Section ---
with st.container(border=True):
    st.markdown("#### Analyze Your Product Data")
    uploaded_file = st.file_uploader(
        "Upload an Excel or CSV file",
        type=['csv', 'xlsx']
    )

    if uploaded_file:
        # Logic to run analysis only once per new file
        if uploaded_file.name != st.session_state.uploaded_filename:
            try:
                with st.spinner(f"Analyzing '{uploaded_file.name}'..."):
                    df = pd.read_csv(uploaded_file) if uploaded_file.type == "text/csv" else pd.read_excel(uploaded_file)
                    st.session_state.user_dataframe = df
                    st.session_state.uploaded_filename = uploaded_file.name
                    # Perform analysis and store the summary in session state
                    st.session_state.data_analysis_summary = perform_pim_analysis(df)
                st.success(f"Successfully analyzed '{uploaded_file.name}'. You can now ask questions about your data.")
            except Exception as e:
                st.error(f"Failed to read or analyze file: {e}")
                st.session_state.data_analysis_summary = None # Clear on failure
    
    if st.session_state.uploaded_filename:
        if st.button(f"Stop Analyzing '{st.session_state.uploaded_filename}'"):
            st.session_state.data_analysis_summary = None
            st.session_state.user_dataframe = None
            st.session_state.uploaded_filename = None
            st.rerun()

st.divider()

# --- Main Query Input ---
with st.form(key="query_form", clear_on_submit=True):
    user_query = st.text_area(
        "**Enter your question:**",
        placeholder="e.g., What is PIM? or What's wrong with my uploaded data?",
        height=100
    )
    submit_button = st.form_submit_button("Get Answer")

if submit_button and embedder:
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        answer = get_assistant_response(user_query)
        st.markdown("### Answer")
        with st.container(border=True):
            st.markdown(answer)

elif not embedder:
    st.error("Application could not start. Please check console logs.")

