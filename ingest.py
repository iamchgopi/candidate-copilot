import chromadb
from sentence_transformers import SentenceTransformer
from resume_data import RESUME_CHUNKS

print("Loading embedding model (first run downloads it, ~90MB, one-time)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to local ChromaDB (saves to ./chroma_db folder)...")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="resume")

print(f"Embedding and storing {len(RESUME_CHUNKS)} resume chunks...")
for chunk in RESUME_CHUNKS:
    embedding = model.encode(chunk["text"]).tolist()
    collection.upsert(
        ids=[chunk["id"]],
        embeddings=[embedding],
        documents=[chunk["text"]],
        metadatas=[{"source": chunk["source"]}],
    )

print("Done! Your resume is now searchable memory.")
print(f"Total chunks stored: {collection.count()}")