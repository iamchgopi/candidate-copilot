import chromadb
from sentence_transformers import SentenceTransformer
from resume_extractor import extract_resume_text, chunk_resume_text

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
db_client = chromadb.PersistentClient(path="./chroma_db")


def ingest_resume(pdf_path, user_id):
    """Extracts, chunks, embeds, and stores a resume under a specific user's collection."""
    text = extract_resume_text(pdf_path)
    chunks = chunk_resume_text(text)

    collection_name = f"resume_{user_id}"
    collection = db_client.get_or_create_collection(name=collection_name)

    for chunk in chunks:
        embedding = embed_model.encode(chunk["text"]).tolist()
        collection.upsert(
            ids=[chunk["id"]],
            embeddings=[embedding],
            documents=[chunk["text"]],
        )

    return len(chunks)


if __name__ == "__main__":
    count = ingest_resume("resume.pdf", user_id="test_user_1")
    print(f"Stored {count} chunks for test_user_1")