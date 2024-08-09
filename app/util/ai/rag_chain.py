import google.generativeai as genai

import urllib
import os
import warnings
from pathlib import Path as p
from pprint import pprint


import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


from app.util.ai.dataset import load_pdf

warnings.filterwarnings("ignore")


GOOGLE_API_KEY = "AIzaSyD5RXtG0TH2WpdDgNy2Bm2P7oFibwPBKYU"


def load_rag_chain_model():
    documents = load_pdf("data/ai")

    print("Load RAG CHAIN begin...")

    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2,
        convert_system_message_to_human=True
    )

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000, chunk_overlap=5000)
    context = "\n\n".join(str(p.page_content) for p in documents)
    text = text_splitter.split_text(context)

    vector_index = Chroma.from_texts(
        text, embeddings).as_retriever(search_kwargs={"k": 10})

    retriever = vector_index
    llm = model

    # Contextualize question
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, just "
        "reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # Answer question
    qa_system_prompt = (
        """
        Kamu adalah JOKO, seorang analis hukum yang membantu menjawab pertanyaan terkait hukum.
        Gunakan konteks yang ditemukan untuk menjawab pertanyaan.
        Jika tidak tahu jawabannya, katakan minta maaf dan katakan bahwa pertanyaan belum dapat dijawab dengan dataset saat ini
        Format jawaban harus dalam format list of object, seperti contoh berikut:
        {{"full_answer": "Rangkuman jawaban secara keseluruhan",
        '"laws": [{{"jawaban": "pasal ini menyebutkan bahwa...", "undang-undang": "Undang-Undang Nomor ...","BAB": "BAB ..." "pasal": "Pasal ...", "ayat": ayat ...}},
        {{"jawaban": "pasal ini menyebutkan bahwa...", "undang-undang": "Undang-Undang Nomor ...","BAB": "BAB ..." "pasal": "Pasal ...", "ayat": ayat ...}},
        {{"jawaban": "pasal ini menyebutkan bahwa...", "undang-undang": "Undang-Undang Nomor ...","BAB": "BAB ..." "pasal": "Pasal ...", "ayat": ayat ...}}, dan seterusnya]}}'
        {context}
        """
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt), MessagesPlaceholder(
                "chat_history"), ("human", "{input}"),
        ]
    )

    # use create_stuff_documents_chain to feed all retrieved context

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(
        history_aware_retriever, question_answer_chain
    )

    print("Load RAG CHAIN success")

    return rag_chain
