from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


def actualizar_embeddings():
    ruta_pdf = "./data/decalogo.pdf"
    loader = PyPDFLoader(ruta_pdf)
    docs = loader.load()

    # Dividir el documento en fragmentos más pequeños que puedan ser manejables
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    chunked_documents = text_splitter.split_documents(docs)

    vectordb = Chroma.from_documents(
        chunked_documents,
        OpenAIEmbeddings(model="text-embedding-3-large", api_key=openai_api_key),
        persist_directory="./chroma_db",
    )

    return vectordb


st.title("Chat de consulta sobre Pokémon Mundo Misterioso")
st.write(
    "Este es un chat que responde preguntas sobre la guía de pokémon mundo misterioso"
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

pregunta = st.text_area("Haz tu pregunta sobre el juego de pokémon mundo misterioso")

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

        print("*"*200)
        print(contexto)
        respuesta = qa_chain.invoke({"input": pregunta, "context": contexto})
        resultado = respuesta.content
        st.write(resultado)
    else:
        st.write("Por favor, ingresa una pregunta antes de enviar.")
