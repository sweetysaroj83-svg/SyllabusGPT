import streamlit as st
from pypdf import PdfReader
import ollama
import re
import subprocess
import tempfile
import os
from PIL import Image

# =========================================================
# PAGE SETTINGS
# =========================================================
st.set_page_config(
    page_title="SyllabusGPT | AI Study Companion",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# UI STYLING ONLY — DOCUMENT / OCR / RETRIEVAL / AI LOGIC
# BELOW IS PRESERVED FROM THE WORKING VERSION.
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --sgpt-bg: #0b1020;
        --sgpt-panel: #121a2d;
        --sgpt-panel-2: #18233a;
        --sgpt-border: rgba(148, 163, 184, 0.20);
        --sgpt-text: #edf2ff;
        --sgpt-muted: #a9b5ce;
        --sgpt-purple: #8b7cff;
        --sgpt-cyan: #61d7ed;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 8% 0%, rgba(91, 75, 190, 0.20), transparent 34%),
            radial-gradient(ellipse at 95% 8%, rgba(40, 172, 202, 0.10), transparent 30%),
            var(--sgpt-bg);
        color: var(--sgpt-text);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 16, 32, 0.88);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #11192b 0%, #0e1525 100%);
        border-right: 1px solid var(--sgpt-border);
    }

    [data-testid="stSidebar"] * {
        color: var(--sgpt-text);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -0.035em;
        color: var(--sgpt-text) !important;
    }

    p, label, [data-testid="stMarkdownContainer"] {
        color: var(--sgpt-text);
    }

    .sgpt-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 0 0 22px 0;
    }

    .sgpt-logo {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 15px;
        color: white;
        font-size: 25px;
        background: linear-gradient(135deg, #7967ff, #39c8e5);
        box-shadow: 0 8px 28px rgba(103, 93, 255, 0.28);
    }

    .sgpt-brand-name {
        font-family: 'Manrope', sans-serif;
        color: #f5f7ff;
        font-size: 1.42rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .sgpt-brand-tag {
        margin-top: 5px;
        color: #9eacc8;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        font-weight: 700;
    }

    .sgpt-hero {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(155, 148, 255, 0.25);
        border-radius: 26px;
        padding: 30px 32px;
        margin-bottom: 24px;
        background: linear-gradient(120deg, rgba(105, 88, 224, 0.20), rgba(42, 174, 202, 0.08) 70%), #121a2d;
        box-shadow: 0 18px 55px rgba(0, 0, 0, 0.16);
    }

    .sgpt-eyebrow {
        color: #a9a1ff;
        font-size: 0.76rem;
        letter-spacing: 0.16em;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .sgpt-hero h1 {
        font-size: clamp(2rem, 4vw, 3.1rem);
        line-height: 1.12;
        margin: 0 0 12px 0;
        background: linear-gradient(90deg, #ffffff, #c8c1ff 55%, #8fe7f4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .sgpt-hero p {
        color: #bac6dd;
        font-size: 1.03rem;
        line-height: 1.7;
        max-width: 760px;
        margin-bottom: 0;
    }

    .sgpt-section-label {
        color: #b8c3dc;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        margin: 22px 0 12px 0;
    }

    div[data-testid="stFileUploader"] section {
        border: 1.5px dashed rgba(139, 124, 255, 0.62);
        border-radius: 18px;
        background: rgba(24, 35, 58, 0.70);
        padding: 14px;
    }

    div[data-testid="stFileUploader"] section:hover {
        border-color: #61d7ed;
        background: rgba(31, 45, 73, 0.85);
    }

    div[data-testid="stFileUploader"] button,
    .stButton > button {
        border: 0;
        border-radius: 12px;
        padding: 0.62rem 1.15rem;
        color: white;
        font-weight: 700;
        background: linear-gradient(100deg, #7666f5, #4e9eea);
        box-shadow: 0 7px 20px rgba(99, 102, 241, 0.20);
        transition: transform 0.15s ease, filter 0.15s ease;
    }

    .stButton > button:hover {
        color: white;
        filter: brightness(1.10);
        transform: translateY(-1px);
        border: 0;
    }

    .stTextInput input, .stTextArea textarea {
        background: #121a2d;
        color: #f3f6ff;
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 13px;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #8b7cff;
        box-shadow: 0 0 0 1px #8b7cff;
    }

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    div[data-testid="stExpander"] {
        background: rgba(18, 26, 45, 0.72);
        border: 1px solid var(--sgpt-border);
        border-radius: 14px;
    }

    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #8b7cff, #61d7ed);
    }

    .sgpt-feature-card {
        background: linear-gradient(145deg, #18233a, #121a2d);
        border: 1px solid var(--sgpt-border);
        border-radius: 17px;
        padding: 17px 18px;
        min-height: 110px;
    }

    .sgpt-feature-title {
        color: #f4f6ff;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .sgpt-feature-copy {
        color: #a9b5ce;
        font-size: 0.90rem;
        line-height: 1.5;
    }

    .sgpt-footer {
        color: #7f8ca8;
        font-size: 0.78rem;
        text-align: center;
        padding-top: 28px;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .sgpt-hero {
            padding: 23px 20px;
            border-radius: 20px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# BRANDED HEADER
# =========================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sgpt-brand">
            <div class="sgpt-logo">✦</div>
            <div>
                <div class="sgpt-brand-name">SyllabusGPT</div>
                <div class="sgpt-brand-tag">YOUR AI STUDY COMPANION</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 📚 Workspace")
    st.caption("Upload a document to start asking questions.")
    st.markdown("---")
    st.markdown("**Supported files**")
    st.caption("PDF · JPG · JPEG · PNG")
    st.markdown("**What you can do**")
    st.caption("• Extract document text\n\n• Read scanned PDFs with OCR\n\n• Ask questions about your content")
    st.markdown("---")
    st.caption("Answers are generated from the uploaded document context.")

st.markdown(
    """
    <div class="sgpt-hero">
        <div class="sgpt-eyebrow">YOUR KNOWLEDGE, SIMPLIFIED</div>
        <h1>Understand any document.</h1>
        <p>Upload a syllabus, notes, PDF, or image. Ask a question and get a clear answer grounded in the content you provide.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="sgpt-section-label">01 / Upload your document</div>', unsafe_allow_html=True)

# =========================================================
# OCR SETTINGS — PRESERVED
# =========================================================
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def run_tesseract(image_path):
    """Run Tesseract directly without importing pytesseract."""
    result = subprocess.run(
        [TESSERACT_PATH, image_path, "stdout"],
        capture_output=True,
        text=True,
        timeout=120,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Tesseract OCR failed.")
    return result.stdout.strip()


def extract_text_from_image(image):
    """Extract text from a JPG, JPEG, or PNG image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_path = temp_file.name
    try:
        image.convert("RGB").save(temp_path)
        return run_tesseract(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def extract_text_from_scanned_pdf_page(pdf_bytes, page_index):
    """Render a scanned PDF page using PyMuPDF and run OCR."""
    import fitz

    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        page = document.load_page(page_index)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_path = temp_file.name
        try:
            pix.save(temp_path)
            return run_tesseract(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    finally:
        document.close()


# =========================================================
# TEXT PROCESSING — PRESERVED
# =========================================================
STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "of", "in",
    "on", "to", "for", "and", "or", "with", "from",
    "how", "why", "when", "where", "which", "who",
    "does", "do", "can", "could", "would", "should",
    "tell", "me", "about", "explain", "please",
    "according", "document", "listed", "mentioned",
}


def get_words(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [word for word in words if word not in STOP_WORDS and len(word) > 1]


def relevance_score(question, page_text):
    """Rank a page using question-word overlap."""
    question_words = get_words(question)
    page_words = get_words(page_text)
    if not question_words or not page_words:
        return 0
    page_word_set = set(page_words)
    score = sum(3 for word in question_words if word in page_word_set)
    q_clean = re.sub(r"\s+", " ", question.lower()).strip()
    p_clean = re.sub(r"\s+", " ", page_text.lower())
    if q_clean and q_clean in p_clean:
        score += 20
    return score


# =========================================================
# QUESTION TYPE HELPERS
# =========================================================
def needs_broad_context(question):
    """Use all extracted pages for questions that need document-wide counting or structure."""
    q = question.lower()
    broad_phrases = (
        "how many", "number of", "count of", "list all", "all units",
        "all chapters", "all modules", "table of contents", "contents page",
        "overall structure", "entire syllabus", "whole document", "summarize the document",
        "summarise the document", "what are the units", "which units", "units are there",
    )
    return any(phrase in q for phrase in broad_phrases)


def find_numbered_headings(pages, heading_type):
    """Find distinct numbered headings and capture titles when printed on the same line."""
    word = re.escape(heading_type)
    pattern = re.compile(
        rf"^\W*{word}\s*[-.:]?\s*(?P<number>[0-9]{{1,3}}|[ivxlcdm]{{1,8}})\b\s*[:.\-–]?\s*(?P<title>.*)$",
        re.IGNORECASE,
    )
    found = {}
    for page in pages:
        for line in page["text"].splitlines():
            match = pattern.match(line.strip())
            if not match:
                continue
            label = match.group("number").upper()
            title = re.sub(r"\s+", " ", match.group("title")).strip(" :-–.\t")
            entry = found.setdefault(label, {"pages": set(), "titles": set()})
            entry["pages"].add(page["page"])
            # Ignore empty titles and generic leftovers that are just punctuation.
            if title:
                entry["titles"].add(title)
    return found


def answer_numbered_heading_count(question, pages):
    """Answer heading-count questions and include titles when extracted text contains them."""
    q = question.lower()
    if not re.search(r"\bhow many\b|\bnumber of\b|\bcount of\b", q):
        return None

    for heading_type in ("unit", "chapter", "module", "section"):
        if re.search(rf"\b{heading_type}s?\b", q):
            headings = find_numbered_headings(pages, heading_type)
            if headings:
                roman_order = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
                labels = sorted(
                    headings,
                    key=lambda value: (0, int(value)) if value.isdigit()
                    else (1, roman_order.index(value) if value in roman_order else value),
                )
                details = []
                for label in labels:
                    titles = sorted(headings[label]["titles"])
                    if titles:
                        details.append(f"{heading_type.title()} {label}: {titles[0]}")
                    else:
                        details.append(f"{heading_type.title()} {label}")
                return (
                    f"I found {len(headings)} numbered {heading_type}(s): "
                    + "; ".join(details)
                    + ". Titles are shown only when they were present on the same line in the extracted text."
                )
    return None

def build_context(question, pages, max_chars=24000):
    """Select useful page text while preserving document-wide context for broad questions."""
    if needs_broad_context(question):
        selected = pages
    else:
        scored_pages = [(relevance_score(question, page["text"]), page) for page in pages]
        scored_pages.sort(key=lambda item: item[0], reverse=True)
        selected = [page for score, page in scored_pages if score > 0][:5]
        if not selected:
            selected = pages[:5]

    chunks = []
    used = 0
    for page in selected:
        chunk = f"--- SOURCE PAGE {page['page']} ---\n{page['text']}"
        remaining = max_chars - used
        if remaining <= 0:
            break
        if len(chunk) > remaining:
            chunk = chunk[:remaining]
        chunks.append(chunk)
        used += len(chunk) + 2
    return "\n\n".join(chunks), selected


# =========================================================
# DOCUMENT UPLOAD — PRESERVED FUNCTIONALITY
# =========================================================
uploaded_file = st.file_uploader(
    "Drop a PDF or image here, or browse your computer",
    type=["pdf", "jpg", "jpeg", "png"],
    help="Supported formats: PDF, JPG, JPEG, PNG",
)

if uploaded_file is not None:
    st.success(f"Ready to process: {uploaded_file.name}")
    pages = []
    filename = uploaded_file.name.lower()

    # PDF TEXT EXTRACTION + OCR
    if filename.endswith(".pdf"):
        try:
            pdf_bytes = uploaded_file.getvalue()
            uploaded_file.seek(0)
            reader = PdfReader(uploaded_file)
            total_pages = len(reader.pages)
            progress = st.progress(0)
            status = st.empty()

            for page_number, pdf_page in enumerate(reader.pages, start=1):
                status.write(f"Processing page {page_number} of {total_pages}…")
                text = pdf_page.extract_text() or ""

                # Use OCR if the PDF page contains no extractable text.
                if not text.strip():
                    try:
                        text = extract_text_from_scanned_pdf_page(pdf_bytes, page_number - 1)
                    except Exception as exc:
                        st.warning(f"OCR failed on page {page_number}: {exc}")

                if text.strip():
                    pages.append({"page": page_number, "text": text.strip()})

                progress.progress(page_number / total_pages)

            status.empty()
            progress.empty()
            st.success(
                f"Processed {total_pages} pages; text extracted from {len(pages)} pages."
            )
        except Exception as exc:
            st.error(f"Could not read the PDF: {exc}")
            st.stop()

    # IMAGE OCR
    else:
        try:
            image = Image.open(uploaded_file)
            with st.spinner("Extracting text from image…"):
                text = extract_text_from_image(image)

            if text.strip():
                pages.append({"page": 1, "text": text.strip()})
                st.success("Image text extracted successfully.")
            else:
                st.warning("No readable text was detected in this image.")
        except Exception as exc:
            st.error(f"Could not process the image: {exc}")
            st.stop()

    # CHECK EXTRACTED TEXT
    if not pages:
        st.error("No readable text could be extracted. Try a clearer image or a text-based PDF.")
        st.stop()

    st.markdown('<div class="sgpt-section-label">02 / Your document is ready</div>', unsafe_allow_html=True)
    left, right = st.columns([1, 1])
    with left:
        st.markdown(
            f"""
            <div class="sgpt-feature-card">
                <div class="sgpt-feature-title">📄 {uploaded_file.name}</div>
                <div class="sgpt-feature-copy">Text extracted and ready for questions.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f"""
            <div class="sgpt-feature-card">
                <div class="sgpt-feature-title">🔎 {len(pages)} page(s) with text</div>
                <div class="sgpt-feature-copy">Ask questions about the contents of this file.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("View extracted document text"):
        for page in pages:
            st.markdown(f"**Page {page['page']}**")
            st.text(page["text"][:6000])

    st.markdown('<div class="sgpt-section-label">03 / Ask your document</div>', unsafe_allow_html=True)
    st.markdown("### 💬 What would you like to know?")
    question = st.text_input(
        "Ask a question about your document",
        placeholder="e.g. Summarize the main topics in this document…",
        label_visibility="collapsed",
    )

    if st.button("✨  Ask SyllabusGPT", type="primary", use_container_width=False):
        if not question.strip():
            st.warning("Please enter a question.")
            st.stop()

        # RETRIEVE RELEVANT CONTEXT
        with st.spinner("Searching your document…"):
            context, ranked_pages = build_context(question, pages)
            if not context.strip():
                st.error("I couldn't extract usable text for answering this question. Check the extracted document text above.")
                st.stop()

        with st.expander("View context sent to AI"):
            st.text(context)

        # For straightforward numbered-heading counts, use the extracted document itself
        # as the source of the count instead of relying on the language model to estimate it.
        heading_count_answer = answer_numbered_heading_count(question, pages)
        if heading_count_answer is not None:
            st.markdown("### 🤖 SyllabusGPT Answer")
            st.markdown(
                f'<div class="sgpt-feature-card">{heading_count_answer}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("### 📄 Source Pages")
            st.write("Relevant pages: " + ", ".join(str(page["page"]) for page in pages))
            st.stop()

        # ASK LOCAL OLLAMA MODEL — PRESERVED
        prompt = f"""
You are SyllabusGPT, a document question-answering assistant.

Answer the student's question using ONLY the document context.

RULES:
1. Answer the exact question asked, using only the document context.
2. Read headings, lists, tables, labels, and short phrases; OCR spacing may be imperfect.
3. Do not infer a count from unrelated numbers, weeks, experiments, credits, or examples.
4. If the context contains only part of the document or the answer cannot be established, say that clearly.
5. Do not invent facts or use outside knowledge to fill gaps.
6. If the answer genuinely is absent, say: "I could not find this information in the uploaded document."
7. Keep the answer concise and mention source page numbers when possible.

DOCUMENT CONTEXT:
{context}

STUDENT QUESTION:
{question}

ANSWER:
"""

        with st.spinner("SyllabusGPT is generating an answer…"):
            try:
                response = ollama.chat(
                    model="llama3.2:3b",
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0},
                )
                answer = response["message"]["content"]
            except Exception as exc:
                st.error(
                    "Could not contact Ollama. Make sure Ollama is running. "
                    f"Details: {exc}"
                )
                st.stop()

        st.markdown("### 🤖 SyllabusGPT Answer")
        st.markdown(
            f'<div class="sgpt-feature-card">{answer}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("### 📄 Source Pages")
        st.write("Relevant pages: " + ", ".join(str(page["page"]) for page in ranked_pages))

else:
    st.markdown(
        """
        <div class="sgpt-section-label">HOW IT WORKS</div>
        <div class="sgpt-feature-card">
            <div class="sgpt-feature-title">① Upload</div>
            <div class="sgpt-feature-copy">Choose a PDF, scanned document, or image.</div>
        </div>
        <br>
        <div class="sgpt-feature-card">
            <div class="sgpt-feature-title">② Extract</div>
            <div class="sgpt-feature-copy">SyllabusGPT extracts readable text from your file.</div>
        </div>
        <br>
        <div class="sgpt-feature-card">
            <div class="sgpt-feature-title">③ Ask and learn</div>
            <div class="sgpt-feature-copy">Ask questions and receive answers based on your document.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="sgpt-footer">SyllabusGPT · Your AI Study Companion</div>',
    unsafe_allow_html=True,
)
