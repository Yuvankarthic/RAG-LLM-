# PIM / MDM AI Assistant

This is a simple, local AI assistant designed to answer questions about Product Information Management (PIM) and Master Data Management (MDM).

## Features
- **Project Focus**: Strictly answers PIM and MDM related questions.
- **Privacy First**: Runs 100% locally on your machine.
- **Open Source**: Uses free, open-source models (Ollama + Mistral).
- **Polite Refusal**: Will not answer off-topic questions (e.g., "What is the capital of France?").

## Prerequisites
1.  **Ollama**: You must have Ollama installed and running.
    -   Download from [ollama.com](https://ollama.com).
    -   Run `ollama run mistral` in your terminal to pull the model.

## Installation
1.  Clone or download this repository.
2.  Navigate to the project folder:
    ```bash
    cd pim-mdm-ai-assistant
    ```
3.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
To start the assitant, run:
```bash
streamlit run app.py
```
The application will open automatically in your default web browser.

## Tech Stack
-   **UI**: Streamlit
-   **LLM**: Ollama (Mistral)
-   **Orchestration**: LangChain
-   **Vector Store**: FAISS
-   **Embeddings**: HuggingFace (Sentence Transformers)
