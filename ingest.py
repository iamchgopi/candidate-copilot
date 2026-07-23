import chromadb
from jd_parser import client as gemini_client
from resume_extractor import extract_resume_text, chunk_resume_text

db_client = chromadb.PersistentClient(path="./chroma_db")


def get_embedding(text):
    """Gets an embedding vector from Gemini's embedding API instead of a local model."""
    response = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return response.embeddings[0].values


def ingest_resume(pdf_path, user_id):
    """Extracts, chunks, embeds (via Gemini), and stores a resume under a specific user's collection."""
    text = extract_resume_text(pdf_path)
    chunks = chunk_resume_text(text)

    collection_name = f"resume_{user_id}"
    collection = db_client.get_or_create_collection(name=collection_name)

    for chunk in chunks:
        embedding = get_embedding(chunk["text"])
        collection.upsert(
            ids=[chunk["id"]],
            embeddings=[embedding],
            documents=[chunk["text"]],
        )

    return len(chunks)


if __name__ == "__main__":
    count = ingest_resume("resume.pdf", user_id="test_user_1")
    print(f"Stored {count} chunks for test_user_1")