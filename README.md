# KTH-GPT

**By Students for Students**

KTH-GPT is a specialized AI assistant designed to help KTH students by providing accurate answers based on course materials and university documents. It utilizes Retrieval-Augmented Generation (RAG) to ground its responses in specific source texts, ensuring relevance and reliability.

## 🚀 Features

-   **RAG-Powered Q&A**: Queries a local vector database (FAISS) with high-retrieval accuracy.
-   **Smart Reranking**: Uses Cross-Encoders (`ms-marco-MiniLM-L-6-v2`) to re-rank search results, ensuring the most relevant context is used.
-   **Advanced Document Processing**: Utilizes `HybridChunker` to intelligently split documents, preserving structure and context.
-   **Terminal-Style Interface**: A retro, terminal web interface for interacting with the AI.
-   **Local LLM Support**: Built to run with local LLMs via Ollama (defaulting to Llama 3.2).
-   **Source Citations**: (Currently disabled) Provides sources for the generated answers to ensure transparency.

## 🛠️ Tech Stack

### Frontend
-   **React**: UI library.
-   **Vite**: Build tool and development server.
-   **CSS**: Custom styling for the terminal aesthetic.

### Backend / AI
-   **Python**: Core programming language.
-   **FastAPI**: API framework for the backend.
-   **LangChain**: Orchestration framework for RAG.
-   **FAISS**: Vector database for efficient similarity search.
-   **Ollama**: Local LLM runner (using `llama3.2`).
-   **Sentence Transformers**: For embedding generation.

## 🏗️ Architecture

![KTH-GPT Architecture](assets/RAG-Architecture.png)

## 📋 Prerequisites

### 1. Install Ollama
Download and install Ollama from [ollama.com](https://ollama.com).

Once installed, pull the required model by running the following command in your terminal:
```bash
ollama pull llama3.2
```

### 2. Environment Setup
-   **Python 3.9+**: Required for the backend.
-   **Node.js & npm**: Required for the frontend.
-   **Virtual Environment**: Highly recommended to isolate dependencies.

**Create and Activate Virtual Environment:**
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. CUDA Requirements
If you do not have a CUDA-enabled GPU (common on macOS or non-NVIDIA systems), please refer to the instructions in `program/RAG_LOCAL/docling_pipeline.py` to configure the document converter appropriately.

## 🏃‍♂️ Usage

### 1. Configure Data Source
You need to provide the documents (e.g., PDFs) that the AI will use as context.
1.  Create a folder (e.g., `canvas_data`) and place your documents inside it.
2.  Open `program/RAG_LOCAL/embeddings.py`.
3.  Update the `DOCUMENTS_FILEPATH` variable to point to your new folder:
    ```python
    DOCUMENTS_FILEPATH = "path/to/your/data_folder"
    ```

### 2. Install Dependencies
Navigate to the project root and install the required Python packages:
```bash
pip install -r program/RAG_LOCAL/requirements.txt
```

### 3. Run the Backend
You can run the backend in two modes:

**API Mode (for Website)**:
Starts the FastAPI server at `http://0.0.0.0:8000`.
```bash
python program/RAG_LOCAL/api.py
```

Once the backend is running, open a new terminal to start the frontend:
```bash
cd website
npm run dev
```
Open your browser and navigate to the local URL provided (usually `http://localhost:5173`).

**CLI Mode (Terminal)**:
Chat with the RAG system directly in your terminal.
```bash
python program/RAG_LOCAL/main.py
```

## 💻 Terminal Commands

The web terminal interface supports various commands to enhance your experience:

### General Commands
- `help` - Display list of available commands
- `about` - Learn more about KTH-GPT
- `contact` - Get contact information and GitHub link
- `clear` - Clear the terminal screen
- `copy` - Copy the last AI response to clipboard

### Theme Customization
Change the terminal appearance with `theme <name>`.

**Popular Themes:**
- `default`, `matrix`, `kth`, `dark`, `retro`, `cyberpunk`
- `chroma`, `purple`, `dracula`, `monokai`
- And many more! Type `help` in the terminal for a full list.

**Example:** `theme chroma`
