import os
from langchain.chat_models import init_chat_model


#Langchain is used to create book assistant agent

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.messages import HumanMessage, AIMessage

# chroma is used as vector DB 
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Keyword retriever
from langchain_community.retrievers import BM25Retriever

# weighted rank fusion function
from langchain_classic.retrievers import EnsembleRetriever


# embedding model used
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")


# Access or create persistent Chroma  vector store (saved on disk)
vector_store = Chroma(
    collection_name="book_collection",  
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",

)

#  global variables for multi-turn use
chat_history =[] 
current_book=None


def LLMquery(book_id,query):
    """
    RAG entry point: answer a query about a specific book.

    - retrieves current book
    - Create a chat model (LLM).
    - Create an agent with middleware that injects retrieved context (prompt_with_context).
    - Invoke the agent on the user message.
    - Return the LLM response content.

    """


    global current_book
    current_book = book_id

    model = init_chat_model("gpt-4.1-mini")

    # Create an agent that use middleware to modify the prompt.
    # Tools will be added in future development
    # Multi turn was too expensive , so it was removed. Will be improved in future
    agent = create_agent(model, tools=[], middleware=[prompt_with_context])
    messages = [HumanMessage(content=query)]

    state = agent.invoke({"messages": messages})
    messages = state.get("messages", [])
    if not messages:
        return ""

    last = messages[-1]
    #print(last.content)
    return last.content



@dynamic_prompt
def prompt_with_context(request: ModelRequest) -> str:
    """
    Middleware hook that returns the system prompt.Performs the retrival step of the RAG pipeline

    - Retrieve overall top k document-formatted chunks from hybrid retriever
    - Inject them into the system message as context
    - The agent then answers the user's question using that context

    """
    global vector_store,current_book
    

    last_query = request.state["messages"][-1].content
    # Retrieve top-k documents (hybrid retrieval).k=5 here
    retrieved_docs  = hybrid_retrieval(last_query,5)

    #Convert retrieved documents into a single context string
    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

    system_message = (
        "You are a helpful multi turn assistant helping a human understand a book`s content. Your response should only be what was asked.Use the following context in your response:"
        f"\n\n{docs_content}"
    )

    return system_message


def hybrid_retrieval(query,k):
    """
    Hybrid retrieval. Performs both BM25 and cosine similarity retrieval. Results are combined using weighted rank funsion

    - Build a cosine similarity retriever from Chroma with a metadata filter on book_id.
    - Fetch all docs for this book_id from Chroma DB using a metadata filter on book_id. to construct BM25 corpus.
    - Create a BM25Retriever over those docs.
    - Combine both retrievers with EnsembleRetriever (weighted).
    - Return ensemble_retriever.invoke(query) -> list[Document].

Notes:
      - BM25 is computed over *all* docs in the book each call, which can be slow
        for large books. You might cache the BM25 retriever per book_id.
    """
    global vector_store,current_book

    # Vector similarity retriever (fast semantic search)
    similarity_search_retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={'k': k,"filter": {"book_id": current_book}}
            )



    raw_docs = vector_store.get(where={"book_id": current_book},include=["documents", "metadatas"],)
    documents = [
            Document(page_content=doc, metadata=meta)
            for doc, meta in zip(raw_docs["documents"], raw_docs["metadatas"])
        ]
    # Build BM25 corpus by pulling all docs for the current book from Chroma vector store
    bm25_retriever = BM25Retriever.from_documents(documents=documents, k=k)

    #Weighted rank fusion: 60% vector similarity, 40% BM25 works well.
    ensemble_retriever = EnsembleRetriever(retrievers=[similarity_search_retriever, bm25_retriever], weights=[0.6, 0.4])
    return ensemble_retriever.invoke(query)
   
