 
# We use the openAI langchain API for text summarizer tool
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


from django.utils.html import strip_tags
from ..models import *
from rest_framework.response import Response
from rest_framework import status





def summarize_all_chapters(book_id):
    """
    Build a running, chapter-by-chapter summary for an entire book using multiple LLM calls.

    Implementation:
      - Load the book chapters from DB
      - Convert each chapter from HTML to plain text (strip_tags)
      - Maintain a running summary string
      - For each chapter:
          * send the running summary + current chapter text to the LLM
          * ask for a short (5-line) summary of only the *new* chapter
          * append it to the running summary
      - Return the final combined summary text

      Note :This iterative refinement process passes as context to LLM ALL previous chapters.Simply passing the last 2-3 chapters as context does not work since book progression to current chapter is not linear.

    """
    try:
        book = Book.objects.get(id=book_id)
        chapters = Chapter.objects.filter(book=book).order_by('number')
    except (Book.DoesNotExist, Chapter.DoesNotExist):
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    chapter_texts = [strip_tags(chapter.content) for chapter in chapters]
    llm = init_chat_model("openai:gpt-4.1-mini")
    summary = " "

    #print(len(chapter_texts))
    chapter_texts.pop(0)

    for c in chapter_texts:

        messages = [
            {
                "role": "system",
                "content": (
                    f"You are summarizing the book '{book.title}' chapter by chapter. "
                    "You will receive a running summary of the previous chapters and "
                    "the full text of the current chapter. "
                    "Write a short 5 line summary of the current chapter that follows "
                    "smoothly from the previous one. Do not repeat old summaries. Mention chapter number before summarizing. "
                    " Most importantly, summarise events from the chapter with greatest importance to the story. "
                    
                ),
            },
            {
                "role": "user",
                "content": (
                    f"SUMMARY OF PREVIOUS CHAPTERS:\n{summary}\n\n"
                    f"CURRENT CHAPTER TEXT:\n{c}\n\n"
                    "SUMMARY OF NEW CHAPTER:"
                ),
            },
        ]

        response = llm.invoke(messages)
        # append to running summary
        summary += f"\n\n{response.content}"

    return summary.strip()

