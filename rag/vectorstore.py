import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "chroma_db"

SKIN_DATA_DIR = BASE_DIR / "data" / "skin"
HAIR_DATA_DIR = BASE_DIR / "data" / "hair"


# --------------------------------------------------
# Embedding Model
# --------------------------------------------------

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_embeddings():
    """
    Create the embedding model used by both
    Skin and Hair knowledge bases.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


# --------------------------------------------------
# Load Documents
# --------------------------------------------------

def load_documents(directory):
    """
    Load all Markdown files from a directory.
    """

    loader = DirectoryLoader(
        str(directory),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={
            "encoding": "utf-8"
        }
    )

    documents = loader.load()

    return documents


# --------------------------------------------------
# Split Documents
# --------------------------------------------------

def split_documents(documents):
    """
    Split large documents into smaller chunks
    for efficient retrieval.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    return splitter.split_documents(documents)


# --------------------------------------------------
# Create Skin Vector Store
# --------------------------------------------------

def create_skin_vectorstore():
    """
    Create or load the Skin Care ChromaDB.
    """

    documents = load_documents(SKIN_DATA_DIR)

    chunks = split_documents(documents)

    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="skin_knowledge",
        persist_directory=str(CHROMA_DIR)
    )

    return vectorstore


# --------------------------------------------------
# Create Hair Vector Store
# --------------------------------------------------

def create_hair_vectorstore():
    """
    Create or load the Hair Care ChromaDB.
    """

    documents = load_documents(HAIR_DATA_DIR)

    chunks = split_documents(documents)

    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="hair_knowledge",
        persist_directory=str(CHROMA_DIR)
    )

    return vectorstore


# --------------------------------------------------
# Load Existing Skin Vector Store
# --------------------------------------------------

def get_skin_vectorstore():

    embeddings = get_embeddings()

    return Chroma(
        collection_name="skin_knowledge",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )


# --------------------------------------------------
# Load Existing Hair Vector Store
# --------------------------------------------------

def get_hair_vectorstore():

    embeddings = get_embeddings()

    return Chroma(
        collection_name="hair_knowledge",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )