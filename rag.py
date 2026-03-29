import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

# ChromaDB Cloud Configuration
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "")
CHROMA_TENANT = os.getenv("CHROMA_TENANT", "default_tenant")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "FarmGPt")

# Jina Embedding Configuration
JINA_API_KEY = os.getenv("JINA_API_KEY", "")

collection_name = "farmgpt_knowledge_jina"

# Use CloudClient for official Chroma Cloud (SaaS)
client = chromadb.CloudClient(
    api_key=CHROMA_API_KEY,
    tenant=CHROMA_TENANT,
    database=CHROMA_DATABASE
)

# Use Jina instead of SentenceTransformers for better multilingual support
jina_ef = embedding_functions.JinaEmbeddingFunction(
    api_key=JINA_API_KEY,
    model_name="jina-embeddings-v3"
)


# Global collection cache
_collection = None

def get_collection():
    global _collection
    if _collection is None:
        _collection = client.get_or_create_collection(
            name=collection_name, 
            embedding_function=jina_ef
        )
    return _collection

def retrieve_context(query: str, n_results: int = 3) -> str:
    """Gets top k relevant passages from the Vector DB"""
    try:
        collection = get_collection()
        count = collection.count()
        if count == 0:
            return ""
            
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, count)
        )
        
        if not results or not results['documents']:
            return ""
            
        # Flatten documents
        documents = [doc for sublist in results['documents'] for doc in sublist]
        if not documents:
            return ""
            
        return "\n---\n".join(documents)
    except Exception as e:
        print(f"RAG Retrieval Error: {e}")
        return ""
