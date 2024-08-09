import os
from langchain.document_loaders import PyPDFLoader


def load_pdf(pdf_folder_path):
    print("Load dataset begin...")
    documents = []
    for file in os.listdir(pdf_folder_path):
        if file.endswith('.pdf'):
            print("Load dataset:", file)
            pdf_path = os.path.join(pdf_folder_path, file)
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
    print("Load dataset success")
    print()
    return documents
