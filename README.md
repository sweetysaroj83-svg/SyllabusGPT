# 📚 SyllabusGPT – AI-Powered Document Question Answering System

### Your AI Study Companion

SyllabusGPT is an AI-powered document question-answering application designed to help students understand academic materials more efficiently. It allows users to upload PDF documents, scanned notes, and images, extract their text, and ask questions to receive context-based answers generated using Large Language Models (LLMs).

The application implements a basic Retrieval-Augmented Generation (RAG) workflow using keyword-based retrieval and Groq LLM integration.

---

## 🎯 Project Objective

The main objective of SyllabusGPT is to simplify the process of studying and accessing information from academic documents.

Students often spend considerable time searching through lengthy textbooks, notes, and syllabus documents to find specific information. SyllabusGPT addresses this challenge by providing an interactive platform where users can ask questions directly about their uploaded documents.

## ✨ Key Features

- **PDF Upload:** Upload academic PDFs and study materials.
- **Image Support:** Upload JPG, JPEG, and PNG files.
- **OCR Technology:** Extract text from scanned PDFs and images using Tesseract OCR.
- **Document Processing:** Extract and organize text page by page.
- **Keyword-Based Retrieval:** Identify relevant document pages based on the user's question.
- **AI-Powered Answers:** Generate contextual responses using Groq LLM.
- **Source Page References:** Display relevant document page numbers.
- **Interactive Interface:** User-friendly interface with a responsive dark-themed design.
- **Multiple Document Formats:** Support for text-based PDFs, scanned PDFs, and images.

## 🧠 RAG Workflow

SyllabusGPT follows a basic Retrieval-Augmented Generation approach.

1. **Document Ingestion:** Users upload PDF files or images.
2. **Text Extraction:** PyPDF extracts PDF text, while Tesseract OCR handles scanned content.
3. **Retrieval:** Keyword matching identifies pages relevant to the user's question.
4. **Context Augmentation:** Retrieved document content is added to the AI prompt.
5. **Generation:** Groq LLM generates an answer grounded in the provided document context.
6. **Response:** The application displays the answer and relevant source pages.

## 🛠️ Technologies Used

| Category | Technology |
|---|---|
| Programming Language | Python |
| Frontend / UI | Streamlit |
| AI / LLM | Groq API |
| Language Model | Groq-hosted LLM |
| PDF Processing | PyPDF |
| OCR | Tesseract OCR |
| Image Processing | Pillow |
| Text Retrieval | Python keyword matching |
| Deployment | Streamlit Community Cloud |
| Version Control | GitHub |

## 🏗️ System Architecture

```text
       User
        |
        v
  Upload PDF / Image
        |
        v
   Document Processing
        |
        v
  Text Extraction / OCR
        |
        v
   Keyword-Based Retrieval
        |
        v
   Relevant Document Context
        |
        v
     Groq LLM API
        |
        v
  Context-Based Answer
        |
        v
  Answer + Source Pages
```

## ⚙️ Application Workflow

1. Open the SyllabusGPT web application.
2. Upload a PDF document or image.
3. Allow the application to extract the document text.
4. Enter a question related to the uploaded content.
5. Click the Ask SyllabusGPT button.
6. Receive an AI-generated answer based on the retrieved document context.
7. View the relevant source pages.

## 🚀 Installation and Setup

### Prerequisites
- Python 3.10 or later
- Git
- Groq API key
- Tesseract OCR

### Step 1: Clone the repository

```bash
git clone https://github.com/sweetysaroj83-svg/SyllabusGPT.git
```

### Step 2: Navigate to the project folder

```bash
cd SyllabusGPT
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

Install Tesseract OCR separately if it is not already installed.

### Step 4: Configure the API key

Create a Streamlit secrets configuration containing:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

Keep your API key private. Never commit it to GitHub.

### Step 5: Run the application

```bash
streamlit run v3.py
```

## 🌐 Live Application

**Live Demo:** https://syllabusgpt-epqs44hhbdmzebk6vtbxnn.streamlit.app

**GitHub Repository:** https://github.com/sweetysaroj83-svg/SyllabusGPT

## 🔮 Future Enhancements

- Semantic search using embedding models.
- Vector database integration for improved retrieval.
- Multi-document question answering.
- Conversation history and memory.
- Automatic quiz and MCQ generation.
- Downloadable summaries and study notes.

## 🎓 Conclusion

SyllabusGPT demonstrates how Generative AI, document processing, OCR, and keyword-based retrieval can be combined to create an intelligent study companion. It helps students access relevant information from academic documents through a simple conversational interface.

**SyllabusGPT – Making Learning Smarter, Simpler, and More Accessible.**
