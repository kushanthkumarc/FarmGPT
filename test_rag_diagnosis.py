from rag import retrieve_context
import json

query = "yes soil waterlogging"
context = retrieve_context(query)
print(f"--- 🧠 RAG Context for: {query} ---")
print(context)
