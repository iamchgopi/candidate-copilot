import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="resume")

query = "experience with payment reconciliation and financial systems"
query_embedding = model.encode(query).tolist()

results = collection.query(query_embeddings=[query_embedding], n_results=3)

print(f"Query: {query}\n")
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"[{meta['source']}] {doc}\n")