from pypdf import PdfReader


def extract_resume_text(pdf_path):
    """Reads a PDF and returns its full text content."""
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text


def chunk_resume_text(full_text):
    """Merges wrapped PDF lines into full bullet points/sentences."""
    lines = full_text.split("\n")
    chunks = []
    current_chunk = ""

    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue

        # Bullet markers or a new section usually signal a new chunk
        starts_new_chunk = cleaned.startswith(("●", "•", "-", "*")) or cleaned.isupper()

        if starts_new_chunk and current_chunk:
            if len(current_chunk) > 30:
                chunks.append({"id": f"chunk_{len(chunks)}", "text": current_chunk.strip()})
            current_chunk = cleaned
        else:
            current_chunk += " " + cleaned

    if current_chunk and len(current_chunk) > 30:
        chunks.append({"id": f"chunk_{len(chunks)}", "text": current_chunk.strip()})

    return chunks

if __name__ == "__main__":
    text = extract_resume_text("resume.pdf")
    chunks = chunk_resume_text(text)
    print(f"Extracted {len(chunks)} chunks from the resume.\n")
    for c in chunks[:5]:
        print(c)