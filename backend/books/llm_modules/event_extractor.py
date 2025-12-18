
from pydantic import BaseModel, Field
from typing import Literal, List
from ..models import *
from bs4 import BeautifulSoup
from openai import OpenAI




class EventInfo(BaseModel):
    """Information about a event in a chapter of a book"""
    event_label: str =Field(description="A  title for the event in less than 4 words" )
    event_summary: str = Field(description="A concise summary of this event in about 2-3 sentences. Do not repeat earlier events; assume the reader already knows what happened before.")
    last_paragraph: int = Field(description="The paragraph number  of the last paragraph that belongs to this event. The event should cover a continuous block of paragraphs, and the next event starts at last_paragraph + 1.")
    
class EventList(BaseModel):
    """List of events that occur in a chapter of book"""
    events: List[EventInfo] = Field(
        description="A list of 1 to 4 events that together cover the whole chapter. The number of events should make sense. Each event should describe a self-contained part of the story. All paragraphs of chapter should be belong to exactly one event with no overlap. ",
    )


def extract_events(book_id):
    """
    Extract a structured list of events for each chapter in a book by identifying the last paragraph in a group of paragraphs that constitute an event

    Pipeline:
      1) Fetch all chapters for the book (ordered by chapter number)
      2) Format chapter HTML into a sequence numbered paragraphs:
           PARAGRAPH 1: <PARAGRAPH 1 CONTENT>
           PARAGRAPH 2: <PARAGRAPH 2 CONTENT>
              ...
      3) pass the transformed chapter text to LLM API where LLM defines markers that splits groups of paragraphs into events 
      4) Parse  the result into EventList and return:
           {"chapter_id": <Chapter.id>, "event_list": <EventList>}


    """
    if not book_id:
        return "No book provided."
    chapters = Chapter.objects.filter(book=book_id).order_by('number')
    client = OpenAI()
    all_events=[]
    for chapter in chapters:
        soup = BeautifulSoup(chapter.content, 'html.parser')
        tag = 0
        for p_tag in soup.find_all('p'):
            tag += 1
            p_text = p_tag.get_text(strip=True)
            raw = f"\n\nPARAGRAPH {tag}: {p_text}"
            p_tag.replace_with(raw)

        chapter_text = str(soup)
        response = client.responses.parse(
    model="gpt-4.1-nano",
    input=[
        {"role": "system", "content": "You are an expert at analysing and extracting book information .You have been provided the current chapter from a book which consists of a sequence of paragraphs along with paragraph number. Your task is to analyse and logically process the chapter into a list of one or more events.Split the chapter into events in a way that feels like a natural breakdown of the story"},
        {
            "role": "user",
            "content": f"Here is the chapter:\n\n {chapter_text}",
        },],text_format=EventList,)
        events: EventList = response.output_parsed
        all_events.append( {"chapter_id":chapter.id,"event_list":events})
    return all_events
        
        
    
           




    
    


