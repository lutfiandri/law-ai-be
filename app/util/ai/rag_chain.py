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
from app.dependency import GOOGLE_API_KEY

warnings.filterwarnings("ignore")


def create_retriever_and_chain():
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
        '"laws": [{{"jawaban": "pasal ini menyebutkan bahwa...", "undang_undang": "Undang-Undang Nomor ...","bab": "BAB ..." "pasal": "Pasal ...", "ayat": ayat ...}},
        {{"jawaban": "pasal ini menyebutkan bahwa...", "undang_undang": "Undang-Undang Nomor ...","bab": "BAB ..." "pasal": "Pasal ...", "ayat": ayat ...}},
        {{"jawaban": "pasal ini menyebutkan bahwa...", "undang_undang": "Undang-Undang Nomor ...","bab": "BAB ..." "pasal": "Pasal ...", "ayat": ayat ...}}, dan seterusnya]}}'
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
    print("Load RAG CHAIN success")

    return history_aware_retriever, question_answer_chain


def create_rag_chain(history_aware_retriever, question_answer_chain):
    rag_chain = create_retrieval_chain(
        history_aware_retriever, question_answer_chain
    )
    return rag_chain


def post_process_answer(answer):
    # contoh answer ="```json\n{\"full_answer\": \"Seseorang yang mengendarai sepeda motor tanpa mengenakan helm yang memenuhi standar nasional Indonesia sebagaimana dimaksud dalam Pasal 106 ayat (8) Undang-Undang Nomor 22 Tahun 2009 tentang Lalu Lintas dan Angkutan Jalan, dipidana dengan pidana kurungan paling lama 1 (satu) bulan atau denda paling banyak Rp250.000,00 (dua ratus lima puluh ribu rupiah).\", \"laws\": [{\"jawaban\": \"Setiap orang yang mengemudikan Sepeda Motor dan Penumpang Sepeda Motor wajib mengenakan helm yang memenuhi standar nasional Indonesia sebagaimana dimaksud dalam Pasal 106 ayat (8) dipidana dengan pidana kurungan paling lama 1 (satu) bulan atau denda paling banyak Rp250.000,00 (dua ratus lima puluh ribu rupiah).\", \"undang-undang\": \"Undang-Undang Nomor 22 Tahun 2009 tentang Lalu Lintas dan Angkutan Jalan\", \"BAB\": \"BAB IX LALU LINTAS\", \"pasal\": \"Pasal 106\", \"ayat\": \"ayat (8)\"}, {\"jawaban\": \"Setiap orang yang mengemudikan Sepeda Motor tidak mengenakan helm standar nasional Indonesia sebagaimana dimaksud dalam Pasal 106 ayat (8) dipidana dengan pidana kurungan paling lama 1 (satu) bulan atau denda paling banyak Rp250.000,00 (dua ratus lima puluh ribu rupiah).\", \"undang-undang\": \"Undang-Undang Nomor 22 Tahun 2009 tentang Lalu Lintas dan Angkutan Jalan\", \"BAB\": \"BAB XX KETENTUAN PIDANA\", \"pasal\": \"Pasal 291\", \"ayat\": \"ayat (1)\"}, {\"jawaban\": \"Setiap orang yang mengemudikan Sepeda Motor yang membiarkan penumpangnya tidak mengenakan helm sebagaimana dimaksud dalam Pasal 106 ayat (8) dipidana dengan pidana kurungan paling lama 1 (satu) bulan atau denda paling banyak Rp250.000,00 (dua ratus lima puluh ribu rupiah).\", \"undang-undang\": \"Undang-Undang Nomor 22 Tahun 2009 tentang Lalu Lintas dan Angkutan Jalan\", \"BAB\": \"BAB XX KETENTUAN PIDANA\", \"pasal\": \"Pasal 291\", \"ayat\": \"ayat (2)\"}]}\n```"

    answer = answer.strip("`")
    answer = answer.strip("json")
    answer = answer.strip("\n")

    return answer
