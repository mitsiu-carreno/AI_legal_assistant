from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
import hashlib
import os
import re
import unicodedata
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Permite todos los orígenes. Cambia esto si necesitas restringir.
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP.
    allow_headers=["*"],  # Permite todos los encabezados.
)

# Global variable to store the vector database
vectordb = None


def hash_document(file_path):
    """Calculate a unique hash for a file based on its content."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as file:
        hasher.update(file.read())
    return hasher.hexdigest()


def clean_text(text):
    # Normalize text to remove accents and special characters
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    # Remove unnecessary special characters and multiple spaces
    text = re.sub(r"[^\w\s.,;:\-\[\]\- \ -]", "", text)
    text = re.sub(r"\.{2,}", "", text)
    text = re.sub(r"\s+", " ", text)
    # Trim unnecessary spaces at the start and end
    text = text.strip()
    return text


def actualizar_embeddings():
    global vectordb
    directory_path = "./data"
    processed_hashes_file = "./processed_hashes.txt"

    # Read previously processed hashes
    if os.path.exists(processed_hashes_file):
        with open(processed_hashes_file, "r") as file:
            processed_hashes = set(file.read().splitlines())
    else:
        processed_hashes = set()

    # Load documents and calculate their hashes
    documents = []
    new_hashes = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(directory_path, file_name)
            file_hash = hash_document(file_path)

            if file_hash not in processed_hashes:  # Process only new documents
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                for doc in docs:
                    # Clean the text of each document before adding it
                    doc.page_content = clean_text(doc.page_content)
                documents.extend(docs)
                new_hashes.append(file_hash)

    if not documents:
        print("No new documents to process.")
        return None

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len,
        separators=["\n", ". ", "? ", "! ", "- "],
    )
    chunked_documents = text_splitter.split_documents(documents)

    # Load or create the Chroma database
    vectordb = Chroma.from_documents(
        chunked_documents,
        OpenAIEmbeddings(model="text-embedding-3-large", api_key=openai_api_key),
        persist_directory="./chroma_db",
    )

    # Save new hashes as processed
    with open(processed_hashes_file, "a") as file:
        file.write("\n".join(new_hashes) + "\n")

    return vectordb


@app.on_event("startup")
async def startup_event():
    """Train embeddings database when the server starts."""
    global vectordb
    print("Initializing embeddings database...")
    vectordb = actualizar_embeddings()  # Assign the result to the global variable


# Define el modelo para la solicitud
class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Handle user questions."""
    global vectordb

    question = request.question  # Extraer el campo 'question'

    if not question:
        raise HTTPException(status_code=400, detail="Please provide a question.")

    if vectordb is None:
        vectordb = Chroma(
            persist_directory="./chroma_db",
            embedding_function=OpenAIEmbeddings(
                model="text-embedding-3-large", api_key=openai_api_key
            ),
        )

    results_similar = vectordb.similarity_search(question, k=10)
    context = ""
    for doc in results_similar:
        context += doc.page_content

    prompt_template = """You are an intelligent assistant specializing in Legal and Information Protection. Answer user questions {input} 
    strictly based on the provided {context}. Do not make assumptions or provide information not included
    in the {context}. Please format your answers clearly and understandably. You may summarize or synthesize 
    the information but try to include as much relevant information as possible."""

    prompt = PromptTemplate.from_template(prompt_template)
    llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=1024, api_key=openai_api_key)
    qa_chain = prompt | llm

    response = qa_chain.invoke({"input": question, "context": context})
    return JSONResponse(content={"answer": response.content})


@app.post("/update_embeddings")
async def update_embeddings_endpoint(background_tasks: BackgroundTasks):
    """Trigger embedding update in the background."""
    background_tasks.add_task(actualizar_embeddings)
    return JSONResponse(
        content={"message": "Embeddings update started in the background."}
    )
