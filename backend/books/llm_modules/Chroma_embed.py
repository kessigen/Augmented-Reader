from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from ..models import Book,Chapter
from django.utils.html import strip_tags


# Embedding model used to convert chunks into vectors
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

#create or get persistent Chroma vector store
vector_store= Chroma(
    collection_name="book_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",

)


def load_book(book_id):

    """
    Convert book text into chunks which are stored as vector embeddings in chroma DB. This function


    - Convert each chapter from HTML to plain text 
    - Wrap each chapter as a LangChain Document with metadata(book_id,chapter_number)   
    - Split documents into  chunks using RecursiveCharacterTextSplitter
    - Store chunks as vector emeddings in chroma
        - computes embeddings
        - stores vectors + text + metadata on disk
    """

    try:
        book = Book.objects.get(id=book_id)
        chapters = Chapter.objects.filter(book=book).order_by('number')
        docs = []
        for chapter in chapters:
            clean = strip_tags(chapter.content)
            docs.append(
                Document(
                    page_content=clean,
                    metadata={
                        "book_id": book.id,
                        "chapter_number": chapter.number,
                    },
                )
            )
    
    except (Book.DoesNotExist, Chapter.DoesNotExist):
        return False

    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  
    chunk_overlap=200,  
    add_start_index=True,  
)
    
    all_splits = text_splitter.split_documents(docs)

    print(f"Split blog post into {len(all_splits)} sub-documents.")

    document_ids = vector_store.add_documents(documents=all_splits)


    