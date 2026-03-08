from typing import List, Optional
import os
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from phi.vectordb.chroma import ChromaDb

class RAGHelper:
    def __init__(self, collection_name: str = "study_materials", persist_directory: str = "./chroma_db"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            self.vectorstore = None
    
    def load_pdf(self, file_path: str) -> bool:
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            chunks = self.text_splitter.split_documents(documents)
            
            self.clear_database()
            
            if self.vectorstore:
                self.vectorstore.add_documents(chunks)
                return True
            return False
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False
    
    def load_text(self, file_path: str) -> bool:
        try:
            loader = TextLoader(file_path)
            documents = loader.load()
            chunks = self.text_splitter.split_documents(documents)
            
            self.clear_database()
            
            if self.vectorstore:
                self.vectorstore.add_documents(chunks)
                return True
            return False
        except Exception as e:
            print(f"Error loading text file: {e}")
            return False
    
    def load_text_content(self, text: str, metadata: dict = None) -> bool:
        try:
            from langchain.schema import Document
            doc = Document(page_content=text, metadata=metadata or {})
            chunks = self.text_splitter.split_documents([doc])
            
            self.clear_database()
            
            if self.vectorstore:
                self.vectorstore.add_documents(chunks)
                return True
            return False
        except Exception as e:
            print(f"Error loading text content: {e}")
            return False
    
    def query(self, question: str, k: int = 4) -> List[str]:
        try:
            if not self.vectorstore:
                return []
            docs = self.vectorstore.similarity_search(question, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return []
    
    def query_with_scores(self, question: str, k: int = 4) -> List[tuple]:
        try:
            if not self.vectorstore:
                return []
            results = self.vectorstore.similarity_search_with_score(question, k=k)
            return [(doc.page_content, score) for doc, score in results]
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return []
    
    def clear_database(self) -> bool:
        try:
            if self.vectorstore:
                client = chromadb.PersistentClient(path=self.persist_directory)
                client.delete_collection(name=self.collection_name)
                self._initialize_vectorstore()
                return True
            return False
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False
    
    def get_document_count(self) -> int:
        try:
            if self.vectorstore:
                collection = self.vectorstore._collection
                return collection.count()
            return 0
        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0
    
    def create_phi_knowledge_base(self) -> Optional[object]:
        try:
            knowledge_base = ChromaDb(
                collection=self.collection_name,
                path=self.persist_directory,
                embedder=self.embeddings
            )
            return knowledge_base
        except Exception as e:
            print(f"Error creating Phi knowledge base: {e}")
            return None