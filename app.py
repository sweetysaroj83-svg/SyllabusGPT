
import io
import os
import re
import math
import tempfile
import subprocess

import streamlit as st
import fitz
import ollama
from pypdf import PdfReader
from PIL import Image


# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="SyllabusGPT",
    page_icon="📚",
    layout="wide"
)

st.title("📚 SyllabusGPT")
st.subheader("Ask Your Curriculum")
st.write(
    "Upload a PDF or image and ask questions about its content."
)

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
MODEL_NAME = "llama3.2:3b"


# =====================================================
# OCR
# =====================================================

def run_tesseract(image_path):
    result = subprocess.run(
        [TESSERACT_PATH, image_path, "stdout"],
        capture_output=True,
        text=True,
        timeout=120,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or "Tesseract OCR failed."
        )

    return result.stdout.strip()


def extract_text_from_image(image):
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ) as temp_file:
            temp_path = temp_file.name

        image.convert("RGB").save(temp_path)
        return run_tesseract(temp_path)

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def extract_text_from_pdf_page(pdf_bytes, page_index):
    temp_path = None

    try:
        with fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as document:
            page = document.load_page(page_index)

            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False
            )

            with tempfile.NamedTemporaryFile(
                suffix=".png", delete=False
            ) as temp_file:
                temp_path = temp_file.name

            pix.save(temp_path)
            return run_tesseract(temp_path)

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# =====================================================
# PDF EXTRACTION — ALL PAGES
# =====================================================

def extract_pdf_pages(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)

    if total_pages == 0:
        raise ValueError("The PDF contains no pages.")

    st.info(f"Total PDF pages detected: {total_pages}")

    pages = []
    progress = st.progress(0)
    status = st.empty()

    for index, pdf_page in enumerate(reader.pages):
        page_number = index + 1

        status.write(
            f"Processing page {page_number} of {total_pages}..."
        )

        try:
            text = pdf_page.extract_text() or ""

            # OCR pages with little extractable text.
            if len(text.strip()) < 30:
                try:
                    ocr_text = extract_text_from_pdf_page(
                        pdf_bytes, index
                    )

                    if len(ocr_text.strip()) > len(text.strip()):
                        text = ocr_text

                except Exception as exc:
                    st.warning(
                        f"OCR failed on page {page_number}: {exc}"
                    )

            if text.strip():
                pages.append({
                    "page": page_number,
                    "text": text.strip()
                })
            else:
                st.warning(
                    f"No readable text detected on page {page_number}."
                )

        except Exception as exc:
            st.warning(
                f"Could not process page {page_number}: {exc}"
            )

        progress.progress((index + 1) / total_pages)

    progress.empty()
    status.empty()

    st.success(
        f"Processed {total_pages} PDF pages; "
        f"text extracted from {len(pages)} pages."
    )

    return pages, total_pages


# =====================================================
# TEXT CHUNKING
# =====================================================

def clean_text(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_chunks(text, chunk_size=1000, overlap=200):
    text = clean_text(text)

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            boundary = max(
                text.rfind("\n", start, end),
                text.rfind(". ", start, end),
                text.rfind("? ", start, end),
                text.rfind("! ", start, end)
            )

            if boundary > start + chunk_size // 2:
                end = boundary + 1

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(start + 1, end - overlap)

    return chunks


def build_chunks(pages):
    chunks = []

    for page in pages:
        for index, text in enumerate(
            split_into_chunks(page["text"]),
            start=1
        ):
            chunks.append({
                "page": page["page"],
                "chunk": index,
                "text": text
            })

    return chunks


# =====================================================
# RETRIEVAL
# =====================================================

STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "of",
    "in", "on", "to", "for", "and", "or", "with",
    "from", "how", "why", "when", "where", "which",
    "who", "does", "do", "can", "could", "would",
    "should", "tell", "me", "about", "please",
    "according", "document", "this", "that", "these",
    "those", "it", "its", "your", "their", "be",
    "was", "were", "has", "have", "had", "list",
    "explain", "describe", "give", "find", "show",
    "mentioned", "mention", "provide", "provided",
    "all", "every", "entire", "complete"
}


def tokenize(text):
    return [
        word
        for word in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if word not in STOP_WORDS and len(word) > 1
    ]


def retrieve_chunks(question, chunks, top_k=8):
    """
    For broad list questions, provide the complete document
    to the answering stage in batches.

    For specific questions, rank chunks by keyword relevance.
    """

    if not chunks:
        return []

    question_lower = question.lower()

    # Broad questions need coverage across the document.
    list_phrases = [
        "all", "list", "every", "entire", "complete",
        "how many", "what are the", "mention all",
        "name the", "which are", "enumerate"
    ]

    asks_for_list = any(
        phrase in question_lower
        for phrase in list_phrases
    )

    if asks_for_list:
        return chunks

    query_words = set(tokenize(question))

    if not query_words:
        return chunks[:top_k]

    tokenized_chunks = [
        tokenize(chunk["text"]) for chunk in chunks
    ]

    total = len(chunks)

    average_length = (
        sum(len(words) for words in tokenized_chunks)
        / max(total, 1)
    )

    document_frequency = {}

    for words in tokenized_chunks:
        for word in set(words):
            document_frequency[word] = (
                document_frequency.get(word, 0) + 1
            )

    scored_chunks = []

    for chunk, words in zip(chunks, tokenized_chunks):
        word_counts = {}

        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        score = 0.0
        length = len(words)

        for word in query_words:
            frequency = word_counts.get(word, 0)

            if frequency == 0:
                continue

            df = document_frequency.get(word, 0)

            inverse_frequency = math.log(
                1 + (total - df + 0.5) / (df + 0.5)
            )

            k1 = 1.5
            b = 0.75

            denominator = frequency + k1 * (
                1 - b + b * length / max(average_length, 1)
            )

            score += inverse_frequency * (
                frequency * (k1 + 1) / denominator
            )

        scored_chunks.append((score, chunk))

    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True
    )

    matches = [
        chunk for score, chunk in scored_chunks
        if score > 0
    ][:top_k]

    return matches if matches else chunks[:top_k]


# =====================================================
# ANSWER GENERATION — BATCH SUPPORT
# =====================================================

def ask_ollama(question, context):
    prompt = f"""
You are SyllabusGPT, a document question-answering assistant.

Answer the question using the document context.

Instructions:
1. Read the entire context supplied for this request.
2. Answer directly and clearly.
3. For list questions, identify every relevant item in the context.
4. Do not stop after the first example when more are present.
5. Include relevant details, numbers, names, and terminology.
6. Cite page numbers when possible.
7. Do not invent information absent from the context.
8. If the context does not answer the question, say so honestly.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={"temperature": 0.1}
    )

    return response["message"]["content"].strip()


def generate_answer(question, relevant_chunks):
    """
    Split large context into batches so broad questions
    do not exceed the model's context capacity.
    Combine findings from every batch when necessary.
    """

    if not relevant_chunks:
        return "No readable document text was found."

    # Small enough contexts can be answered in one request.
    total_chars = sum(
        len(chunk["text"]) for chunk in relevant_chunks
    )

    if total_chars <= 10000:
        context = "\n\n".join(
            f"[Page {chunk['page']}]\n{chunk['text']}"
            for chunk in relevant_chunks
        )
        return ask_ollama(question, context)

    # For long documents, answer using consecutive batches.
    batch_size = 6
    batch_answers = []

    for start in range(0, len(relevant_chunks), batch_size):
        batch = relevant_chunks[start:start + batch_size]

        context = "\n\n".join(
            f"[Page {chunk['page']}]\n{chunk['text']}"
            for chunk in batch
        )

        batch_question = (
            question
            + "\nReport all relevant information in this batch. "
            "Do not assume this batch contains the entire document."
        )

        answer = ask_ollama(batch_question, context)

        batch_answers.append(
            f"Batch {start // batch_size + 1}:\n{answer}"
        )

    combined_context = "\n\n".join(batch_answers)

    # Consolidate duplicate findings without losing distinct items.
    return ask_ollama(
        "Answer the original question using all the findings below. "
        "Combine duplicate items, preserve distinct items, and do not "
        "omit relevant information. Original question: " + question,
        combined_context
    )


# =====================================================
# MAIN APPLICATION
# =====================================================

uploaded_file = st.file_uploader(
    "📄 Upload a PDF or image",
    type=["pdf", "jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name.lower()

    try:
        with st.spinner("Processing your document..."):

            if filename.endswith(".pdf"):
                pages, total_pages = extract_pdf_pages(file_bytes)

            else:
                image = Image.open(io.BytesIO(file_bytes))
                text = extract_text_from_image(image)

                pages = []

                if text.strip():
                    pages.append({
                        "page": 1,
                        "text": text.strip()
                    })

                total_pages = 1
                st.info("Total image pages detected: 1")

        if not pages:
            st.error("No readable text was extracted.")
            st.stop()

        chunks = build_chunks(pages)

        st.caption(
            f"Pages detected: {total_pages} | "
            f"Pages with text: {len(pages)} | "
            f"Text chunks: {len(chunks)}"
        )

        with st.expander("📖 View extracted document text"):
            for page in pages:
                st.markdown(f"**Page {page['page']}**")
                st.text(page["text"])

        question = st.text_input(
            "💬 Ask any question about your document",
            placeholder="Ask a question about any section..."
        )

        if st.button("Ask SyllabusGPT", type="primary"):

            if not question.strip():
                st.warning("Please enter a question.")

            else:
                try:
                    with st.spinner(
                        "Searching and preparing your answer..."
                    ):
                        relevant_chunks = retrieve_chunks(
                            question, chunks, top_k=8
                        )

                        answer = generate_answer(
                            question, relevant_chunks
                        )

                    st.subheader("🤖 SyllabusGPT Answer")
                    st.markdown(answer)

                    source_pages = sorted({
                        chunk["page"]
                        for chunk in relevant_chunks
                    })

                    st.caption(
                        "Retrieved source pages: "
                        + ", ".join(map(str, source_pages))
                    )

                    with st.expander("🔎 View context sent to AI"):
                        for chunk in relevant_chunks:
                            st.markdown(
                                f"**Page {chunk['page']} — "
                                f"Chunk {chunk['chunk']}**"
                            )
                            st.write(chunk["text"])

                except Exception as exc:
                    st.error(
                        "Could not generate an answer. "
                        "Make sure Ollama is running and the "
                        f"'{MODEL_NAME}' model is installed. "
                        f"Details: {exc}"
                    )

    except Exception as exc:
        st.error(f"Document processing failed: {exc}")
