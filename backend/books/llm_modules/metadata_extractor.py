from pydantic import BaseModel, Field
from typing import Literal, List
from ..models import *


from django.utils.html import strip_tags

# OpenAI  client api
from openai import OpenAI



class ChapterMood(BaseModel):
    mood: Literal["neutral", "hopeful","tense", "sad","dark"] = Field("neutral",
        description=("The overall atmosphere or mood of events occurring in the chapter. "
            "Defaults to 'neutral' if mood does not clearly match any other option."
        ),
    )

class BookMetaData(BaseModel):
    """Information about a novel"""
    main_genre:  List[str] = Field(description="list the main genres to which the book belongs to.Examples are fantasy, sci-fi, historical, ...")
    time_period: str = Field(description="the approximate time period in which novel takes place.Examples are Victorian era, near-future, post-apocalyptic, unspecified ")
    primary_setting :str = Field(description="a short label for the type of background or place where most of the story happens")
    synopsis : str = Field(description="a 4 line synopsis of the story")
    MoodList :List[ChapterMood] = Field(description="Each paragraph of summary corresponds to book chapter.One entry in list per chapter, in chapter order.")


    
def get_book_metadata(book_id):
    """
    extarct structured metadata for the book content in general using its full  summary.

    
    - Load Book from DB
    - OpenAI API call with a the book summary as context
    - Parse and return the model output directly into the BookMetaData Pydantic model

    
    """
    book = Book.objects.get(id=book_id)
    client = OpenAI()
    title=book.title

    response = client.responses.parse(
    model="gpt-4.1-nano",
    input=[
        {"role": "system",
          "content": f"You are an expert at analysing and extracting book information .You have been provided the chapter by chapter summary of the book {title}. Your task is to analyse the summary and logically infer book metadata from it."},
        {
            "role": "user",
            "content": f"Here is the book summary:\n\n {book.summary}",
        },],text_format=BookMetaData,)
    
    metadata: BookMetaData = response.output_parsed
    
    return metadata