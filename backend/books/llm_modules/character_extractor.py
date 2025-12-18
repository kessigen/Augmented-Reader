from pydantic import BaseModel, Field
from typing import Literal, List
from ..models import *
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from django.utils.html import strip_tags


class CharacterInfo(BaseModel):
    """Information about a character"""
    name: str = Field(description="The name of the charcter in the story")
    role: Literal["protagonist", "antagonist","supporting character"] = Field(description="The role of the character in the story")
    age: int = Field(description="The age of the character")
    gender : str = Field(description="The gender of the character in the book")
    personality: str =Field(description="The personality of the character in the book described in 4 lines")
    appearance: str =Field(description="A detailed physical description of the character`s physical appearance and look in 5 lines. A reader should be able to visualise the character based on just this description")
    bio : str = Field(description="A 4 line bio of the character")
    chapters_appeared : List[int] = Field(description="list of c_id in which the character appeared")
    
class CharacterList(BaseModel):
    """List of characters"""
    Characters: List[CharacterInfo] = Field(
        description="List of about to 6 elements each containing a character`s information",
    )

def character_summary(book_id):
    """

    Create a running human-readable  list of main characters in a bbook by reading chapters one-by-one.

    Pipeline:
      - Convert each chapter HTML to  plain text
      - Maintain 'character_summary' text that gets updated each chapter
      - Each loop (new chapter):
          - send current chapter text + existing character list to the LLM
          - ask the LLM to extract newly discovered characters and swap out existing characters if needed (max 6 characters)
          - Since LLM has no access to previous chapters when choosing to replace characters, we introduce a field in running list called confidence score where the LLM scores how sure it is a character it chooses is relevant to story. This score can then be used to switch out existing irrelevant characters
      - Returns the final summarized character list as plain text 

    """


    if not book_id:
        return "No book provided."
    book = Book.objects.get(id=book_id)
    #print(book)
    chapters = Chapter.objects.filter(book=book_id).order_by('number')
    chapter_texts = [strip_tags(chapter.content) for chapter in chapters]
    
    llm = init_chat_model("gpt-4.1-mini")
    
    character_summary=''
    chapter_texts.pop(0)
    for c in chapter_texts:

        messages = [
            {
                "role": "system",
                "content": (
                    f"Your task is to identify fictional characters from the book '{book.title}' and extracting and summarizing their information from a book, chapter by chapter. "
                    "You will receive the full text of the current chapter and a running list of characters identified from the previous chapters."
                    f"Analyse the current chapter to (1) add new  characters   and (2) update the information for characters in the running list only if you find new information about them."
                    "There can be at most 6 characters in the list.Keep adding new chracters to list if it contains less than 6.If you find a new relevant character in current chapter and running list is full, REPLACE an existing character with lowest confidence score with the new character ONLY if you think they are more relevant than the existing character( Use the confidence_score values of the existing characters to decide which one to remove,i.e remove the lowest-confidence character) OTHERWISE ignore new character."
                   "Your goal is to return only an updated list after making all changes relevant to the new chapter"
                   "If you do not know some attribute for a character,you can set it to ' ' "
                   "If current chapter is not a story chapter but a preface or something similar, ignore and return unchanged list "
                  "Return only the updated list as a clear, human-readable summary. "
            "using the pseudo-structured format below for each list element. Keep it concise but detailed:\n\n"
            "CHARACTER 1:\n"
            "    name: <name>\n"
            "    role: <protagonist | antagonist | supporting character>\n"
            "    age: <age>\n"
            "    gender: <gender>\n"
            "    personality: <4 lines describing personality>\n"
            "    appearance: <5 lines detailed description of physical appearance.A reader should be able to visualise the character based on just this description>\n"
            "    bio: <4-line biography>\n"
            "    chapters_appeared: [<list of chapter numbers>]\n"
            "    confidence_score: <score between 0 and 1, describing how confident you are that this character is relevant to the story> \n\n"
           
                    
                ),
            },
            {
                "role": "user",
                "content": (
                    f"agent response for list of PREVIOUSLY IDENTIFIED CHARACTERS:\n{character_summary}\n\n"
                    f"CURRENT CHAPTER TEXT:\n{c}\n\n"
                    "UPDATED LIST OF CHARACTERS:"
                ),
            },
        ]
        character_summary = llm.invoke(messages).content
    
    print(character_summary)
    return character_summary
    


def set_characters(book_id):

    """
    Convert the final character list text into a pydantic CharacterList object.

    
    Note: confidence_score is ignored during parsing since we do not need it anymore
    """

    if not book_id:
        return "No book provided."
    character_list_text=character_summary(book_id)
    llm = init_chat_model("openai:gpt-4.1")
    extractor = llm.with_structured_output(CharacterList)
    
    clist = CharacterList(Characters=[])

    messages = [
            {
                "role": "system",
                "content": (
                    "Character information for about 6 fictional book characters of a book has been identified and summarised by an LLM" 
                "and is provided below.Return a CharacterList containing that information. Ignore the confidence score"
                ),
            },
            {
                "role": "user",
                "content": (
                    f" agent response summary of PREVIOUSLY IDENTIFIED CHARACTERS:\n{character_list_text}\n\n"
                    
                ),
            },
        ]

 
    clist = extractor.invoke(messages)   
  
    print("Extracted Characters:", [c.name for c in clist.Characters])
    return clist
        

    
class Relationship(BaseModel):
    source: str = Field(description="Character name (must match CharacterInfo.name)")
    target: str = Field(description="Character name (must match CharacterInfo.name)")
    label: str = Field(description="Short label to show on the edge, e.g., 'friends', 'rivals', 'mentor'")  


class RelationshipList(BaseModel):
    relationships: List[Relationship] = Field(
        description="List of relationships between characters",
    )

def set_character_relationships(book_id):
    if not book_id:
        return "No book provided."
    book = Book.objects.get(id=book_id)
    context_1= book.summary

    characters = Character.objects.filter(book_id=book_id)
    list=[]
    for c in characters:
        details = (
            f"Name: {c.name}\n"
            f"Role: {c.role}\n"
            f"Age: {c.age if c.age is not None else 'unknown'}\n"
            f"Gender: {c.gender or 'unspecified'}\n\n"
            f"Personality:\n{c.personality or 'N/A'}\n\n"
            f"Appearance:\n{c.appearance or 'N/A'}\n\n"
            f"Bio:\n{c.bio or 'N/A'}\n"
        )
        list.append(details)
    context_2="\n\n".join(list)
    llm = init_chat_model("openai:gpt-4.1-mini")
    extractor = llm.with_structured_output(RelationshipList)
    rlist = RelationshipList(relationships=[])


   
    
    messages = [
  {
    "role": "system",
    "content": (
      "You are a  literature expert. Your task is to extract  relationships between characters "
      "using only the book context, and output ONLY  a RelationshipList object that conforms exactly to the "
      " \n\n"
      "INSTRUCTIONS :\n"
      "source and target MUST be character names that appear in CONTEXT 2.\n"
      "label must be a short relationship label suitable for showing on an edge in a network graph "
      "(e.g., 'friends', 'rivals', 'mentor', 'family', 'allies', 'owner', 'enemy').\n"    
      "Do not invent new characters.\n"
      "Only include clear and meaningful relationships.if they exist.\n"
      " If direction is unclear, keep it symmetric (just one edge)."
    ),
  },
  {
    "role": "user",
    "content": (
      f"BOOK TITLE: {book.title}\n\n"
      "CONTEXT 1 (book summary, chapter-by-chapter):\n"
      f"{context_1}\n\n"
      "CONTEXT 2 (major characters with attributes):\n"
      f"{context_2}\n\n"
      " RelationshipList JSON object:\n\n"
    ),
  },
]
        
    rlist = extractor.invoke(messages)  

    return rlist
