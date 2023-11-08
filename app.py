import os
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """Extract text from a single PDF file."""
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

def create_chroma_vector_store(pdf_directory, limit=20):
    """Create a chroma vector store with text from PDF files."""
    chroma_vector_store = []
    for entry in os.scandir(pdf_directory):
        if entry.is_file() and entry.name.endswith('.pdf'):
            pdf_text = extract_text_from_pdf(entry.path)
            chroma_vector_store.append(pdf_text)
            if len(chroma_vector_store) >= limit:
                break  # Stop if we have reached the limit
    return chroma_vector_store

# Specify the directory where your PDF files are located
pdf_directory = './data/'

# Create the chroma vector store
chroma_store = create_chroma_vector_store(pdf_directory)

# Save each document to a separate text file
for idx, document_text in enumerate(chroma_store):
    with open(f'document_{idx+1}.txt', 'w', encoding='utf-8') as f:
        f.write(document_text)

print(f"Chroma vector store saved with {len(chroma_store)} documents.")
