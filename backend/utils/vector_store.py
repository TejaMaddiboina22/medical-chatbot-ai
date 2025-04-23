import json
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import sys

backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from config.config import Config


def load_medical_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    qa_pairs = []
    for entry in data:
        disease = entry['disease']  
        description = entry['answer']  

        # Generate the questions for each disease
        disease_questions = [
            f"What is {disease}?",
            f"What are the symptoms of {disease}?",
            f"What are the causes of {disease}?",
            f"What are the treatments for {disease}?",
        ]
        
        # Create a QnA pair for each question
        for question in disease_questions:
            qa_pairs.append({
                "question": question,
                "answer": description,  
                "disease": disease
            })
    
    return qa_pairs


def create_documents_from_data(data):
    # Convert the QnA pairs into LangChain Document objects.
    documents = []
    for qa_pair in data:
        # Create a document with the question and answer
        doc = Document(
            page_content=f"Question: {qa_pair['question']}\n\nAnswer: {qa_pair['answer']}",
            metadata={"disease": qa_pair["disease"]}
        )
        documents.append(doc)
    return documents


def initialize_vector():
    # Knowledge base and vector store paths
    kb_path = os.path.join(backend_dir, 'data', 'medical_kb', 'structured_data.json')
    vector_store_path = os.path.join(backend_dir, 'data', 'vector_store')
    
    # Check if the vector store already exists
    if os.path.exists(os.path.join(vector_store_path, 'index.faiss')):
        embeddings = HuggingFaceEmbeddings(model_name="pritamdeka/S-PubMedBert-MS-MARCO")
        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        return vector_store
    
    medical_data = load_medical_data(kb_path)
    medical_doc = create_documents_from_data(medical_data)
    
    hf_embedding = HuggingFaceEmbeddings(model_name="pritamdeka/S-PubMedBert-MS-MARCO")
    
    # Initialize FAISS vector store and populates with embedded docs 
    vector_store = FAISS.from_documents(medical_doc, hf_embedding)
    
    os.makedirs(Config.VECTOR_STORE_PATH, exist_ok=True)
    vector_store.save_local(Config.VECTOR_STORE_PATH)
    
    return vector_store


if __name__ == "__main__":
    initialize_vector()