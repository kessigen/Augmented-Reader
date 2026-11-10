from pydantic import BaseModel, Field
from typing import Literal, List
from ..models import *

# OpenAI client API
from openai import OpenAI



class ChapterMood(BaseModel):
    mood: Literal["neutral", "hopeful","tense", "sad","dark"] = Field("neutral",
        description=("The overall atmosphere or mood of events occurring in the chapter. "
            "Defaults to 'neutral' if mood does not clearly match any other option."
        ),
    )

class BookMetaData(BaseModel):
    """Information about a novel"""
    main_genre:  List[str] = Field(description="List the main genres the book belongs to. Examples are fantasy, sci-fi, historical, ...")
    time_period: str = Field(description="The approximate time period in which the novel takes place. Examples are Victorian era, near-future, post-apocalyptic, unspecified ")
    primary_setting :str = Field(description="A short label for the type of background or place where most of the story happens")
    synopsis : str = Field(description="A 4-line synopsis of the story")
    MoodList :List[ChapterMood] = Field(description="Each paragraph of the summary corresponds to a book chapter. One entry in list per chapter, in chapter order.")


    
def get_book_metadata(book_id):
    """
    Extract structured metadata for the book content in general using its full summary.

    
    - Load Book from DB
    - OpenAI API call with the book summary as context
    - Parse and return the model output directly into the BookMetaData Pydantic model

    
    """
    book = Book.objects.get(id=book_id)
    client = OpenAI()
    title=book.title

    response = client.responses.parse(
    model="gpt-4.1-nano",
    input=[
        {"role": "system",
          "content": f"You are an expert at analysing and extracting book information. You have been provided the chapter by chapter summary of the book {title}. Your task is to analyse the summary and logically infer book metadata from it."},
        {
            "role": "user",
            "content": f"Here is the book summary:\n\n {book.summary}",
        },],text_format=BookMetaData,)
    
    metadata: BookMetaData = response.output_parsed
    
    return metadata