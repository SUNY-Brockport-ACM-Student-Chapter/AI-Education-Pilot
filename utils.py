import json
import os

import chromadb
import PyPDF2
import streamlit as st
import yaml
from chromadb.utils import embedding_functions
from openai import OpenAI


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


def embed_content_in_chunks(content, ai_client):
    chunk_size = 800
    chunk_overlap = 200
    chunks = [
        content[i : i + chunk_size]
        for i in range(0, len(content), chunk_size - chunk_overlap)
    ]

    embeddings = []
    for chunk in chunks:
        response = ai_client.embeddings.create(
            input=chunk, model="text-embedding-ada-002"
        )
        embeddings.append(response.data[0].embedding)
    return chunks, embeddings


def load_questions_and_answers(json_path):
    with open(json_path, "r") as file:
        data = json.load(file)
    questions = {k: f"{k}: {v}" for k, v in data["questions"].items()}
    return questions, data["answers"]


def get_relevant_content(collection, user_answer, actual_answer, question):
    combined_query = f"{question} {user_answer} {actual_answer}"
    results = collection.query(query_texts=[combined_query], n_results=3)
    relevant_content = "\n\n".join(results["documents"][0])
    return relevant_content if relevant_content else ""


def load_prompts():
    with open("prompts.yaml", "r") as file:
        return yaml.safe_load(file)


def get_feedback(ai_client, user_answer, question, relevant_content, actual_answer):
    prompts = load_prompts()

    feedback_prompt = prompts["feedback_prompt"].format(
        question=question,
        user_answer=user_answer,
        actual_answer=actual_answer,
        relevant_content=relevant_content,
    )
    response = ai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": feedback_prompt},
        ],
    )
    return response.choices[0].message.content


@st.cache_resource
def get_or_create_chroma_collection(_db_client, module_content_fp, _ai_client):
    collection_name = "module_content"

    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-ada-002"
    )

    try:
        collection = _db_client.get_collection(
            name=collection_name, embedding_function=embedding_function
        )
        print("Using existing ChromaDB collection.")
    except chromadb.errors.InvalidCollectionException:
        print("No existing ChromaDB collection found. Creating a new one...")
        pdf_text = extract_text_from_pdf(module_content_fp)
        chunks, embeddings = embed_content_in_chunks(pdf_text, _ai_client)
        collection = _db_client.create_collection(
            name=collection_name, embedding_function=embedding_function
        )
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=[f"embedding_{i}" for i in range(len(embeddings))],
        )
        print("New collection created and embeddings added to ChromaDB.")

    return collection
