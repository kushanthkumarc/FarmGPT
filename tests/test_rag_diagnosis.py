import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag import retrieve_context
import json

query = "yes soil waterlogging"
context = retrieve_context(query)
print(f"--- 🧠 RAG Context for: {query} ---")
print(context)
