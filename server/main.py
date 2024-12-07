from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
import hashlib
import streamlit as st
import os
from dotenv import load_dotenv
import re
import unicodedata

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


def hash_document(file_path):
    """Calcula un hash único para un archivo basado en su contenido."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as file:
        hasher.update(file.read())
    return hasher.hexdigest()


def clean_text(text):
    # Normalizar texto para eliminar acentos y caracteres especiales
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    # Eliminar caracteres especiales innecesarios y múltiples espacios
    text = re.sub(r"[^\w\s.,;:\-\[\]\- \ -]", "", text)
    text = re.sub(r"\.{2,}", "", text)
    text = re.sub(r"\s+", " ", text)
    # Eliminar espacios innecesarios al inicio y al final
    text = text.strip()
    return text


def actualizar_embeddings():
    directory_path = "./data"
    processed_hashes_file = "./processed_hashes.txt"

    # Leer los hashes procesados previamente
    if os.path.exists(processed_hashes_file):
        with open(processed_hashes_file, "r") as file:
            processed_hashes = set(file.read().splitlines())
    else:
        processed_hashes = set()

    # Cargar los documentos y calcular sus hashes
    documents = []
    new_hashes = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(directory_path, file_name)
            file_hash = hash_document(file_path)

            if file_hash not in processed_hashes:  # Solo procesar documentos nuevos
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                for doc in docs:
                    # Limpiar el texto de cada documento antes de agregarlo
                    doc.page_content = clean_text(doc.page_content)
                documents.extend(docs)
                new_hashes.append(file_hash)

    if not documents:
        print("No hay documentos nuevos para procesar.")
        return None

    # Dividir en fragmentos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len,
        separators=["\n", ". ", "? ", "! ", "- "],
    )
    chunked_documents = text_splitter.split_documents(documents)

    # Cargar o crear la base de datos Chroma
    vectordb = Chroma.from_documents(
        chunked_documents,
        OpenAIEmbeddings(model="text-embedding-3-large", api_key=openai_api_key),
        persist_directory="./chroma_db",
    )

    # Guardar los hashes nuevos como procesados
    with open(processed_hashes_file, "a") as file:
        file.write("\n".join(new_hashes) + "\n")

    return vectordb


st.title("Chat de consulta sobre Legalidad y Protección de la Información")
st.write(
    "Este es un chat que responde preguntas sobre legalidad y protección de la información"
)

if st.button("Actualizar Embeddings"):
    vectordb = actualizar_embeddings()
    st.write("Embeddings actualizados correctamente.")

prompt_template = """Eres un agente de ayuda inteligente especializada en Legalidad y Protección de la Información. Responde las preguntas de los usuarios {input} 
basándote estrictamente en el {context} proporcionado. No hagas suposiciones ni proporciones  información que no esté incluida
en el {context}. Trata de dar un formato bien estructurado y entendible a tus respuestas por favor. Puedes hacer resumenes o
sintesis de la información, pero trata de incluir la mayor cantidad de información importante posible."""

prompt = PromptTemplate.from_template(prompt_template)
llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=1024, api_key=openai_api_key)
qa_chain = prompt | llm

pregunta = st.text_area(
    "Haz tu pregunta sobre la legalidad y protección de la información"
)

if st.button("Enviar"):
    if pregunta:
        vectordb = Chroma(
            persist_directory="./chroma_db",
            embedding_function=OpenAIEmbeddings(
                model="text-embedding-3-large", api_key=openai_api_key
            ),
        )
        resultados_similares = vectordb.similarity_search(pregunta, k=10)
        contexto = ""
        for doc in resultados_similares:
            contexto += doc.page_content

        print("*" * 200)
        print(contexto)
        respuesta = qa_chain.invoke({"input": pregunta, "context": contexto})
        resultado = respuesta.content
        st.write(resultado)
    else:
        st.write("Por favor, ingresa una pregunta antes de enviar.")
