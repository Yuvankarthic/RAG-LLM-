from langchain_community.chat_models import ChatOllama

llm = ChatOllama(
    model="mistral",
    temperature=0,
    timeout=60
)

print("Calling model...")
response = llm.invoke("Say hello in one sentence.")
print("Response:", response.content)
