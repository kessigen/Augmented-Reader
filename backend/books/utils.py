import os
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Book,Chapter,Event

from bs4 import BeautifulSoup
from django.utils.html import strip_tags
from .serializers import CharacterSerializer
#from PIL import Image, ImageDraw, ImageFont

#import  llm moduless
from books.llm_modules.summarizer import *

# import model for character object
from .models import Character as CharacterModel



def save_characters_to_db(book, character_list):
    """
    Saves extracted characters to DB and optionally generates a portrait image.

    Inputs:
      - book: Book object
      - character_list: list of generated character objects

    For each character:
      - get_or_create new character into DB 
      - store  field attributes  with  fallbacks (role, age, personality, etc.)
      - generate an image if the row was just created or the row exists but has no image yet
    """
    #imported inside to avoid circular import error
    from books.llm_modules.image_gen import generate_character_image

    for ci in character_list.Characters:
        character, created = CharacterModel.objects.get_or_create(
            book=book,
            name=ci.name,
            defaults={
                "role": ci.role or "supporting character",
                "age": ci.age if isinstance(ci.age, int) else None,
                "gender": ci.gender or "",
                "personality": ci.personality or "",
                "appearance": ci.appearance or "",
                "bio": ci.bio or "",
                "chapters_appeared": ci.chapters_appeared or [],
            },
        )
        if created or not character.image:
            generate_character_image(character)

def save_events_to_db(book, event_list):
    """
    Saves extracted events to DB AND edits chapter HTML to insert placeholders.

    Inputs:
      - book: Book object
      - event_list: list of events for every chapter 
      
    For each chapter:
      - fetch the Chapter row by its DB id
      - enumerate events (index starts at 1 per chapter)
      - edit the chapter HTML to add a placeholder div at the event anchor paragraph
      - create an Event row (chapter, number, start_index, summary, label)
    """

    for chapter_events in event_list:
        index=0
        ch = Chapter.objects.get(book=book, id=chapter_events["chapter_id"])

        for ev in chapter_events["event_list"].events:
            
            index+=1
            edit_chapter(ch,ev,index)
            Event.objects.create(
            chapter = ch,
            number=index,
            start_index=ev.last_paragraph,
            summary=ev.event_summary,  
            label=ev.event_label
        )



def edit_chapter(chapter,event,event_index):
    """
    Inserts an HTML placeholder into a chapter at the paragraph indicated by event.last_paragraph.
    Currently all paragraphs in chapter have paragraph number. This number is used to identify pointers for event scenes.
    Once anchors for event are added, extra paragraph index are removed.This  lets the frontend  locate event anchors and swap for scene image generation

    - append a div placeholder inside the target <p>:
        <div id="ev{event_index}">PLACEHOLDER FOR IMAGE {event_index}</div>

    """
    event_position=event.last_paragraph
    soup = BeautifulSoup(chapter.content, 'html.parser')
    p_tags = soup.find_all("p")
    total = len(p_tags)
    if total == 0:
        print("No <p> tags in this chapter, skipping event.")
        print("*********************")
        return
    if event_position < 1:
        print("Invalid last_paragraph (<1), skipping.")
        print("*********************")
        return
    
    if event_position > total:        
        event_position = total
    
    p_tag =p_tags[event_position - 1]
    div = soup.new_tag("div", id=f"ev{event_index}")
    div.string = f"PLACEHOLDER FOR IMAGE {event_index}"
    p_tag.append(div)
    chapter.content=str(soup)
    chapter.save()
    

def get_chapter_summary(book_id, chapter_id):
    """
    Returns a "summary up to this chapter" text. Just truncates the full text summary (which was already generasted during upload time) up to current chapter
    """

    book = Book.objects.get(id=book_id)
    full_summary=book.summary
    paragraphs = [p.strip() for p in full_summary.split("\n\n") if p.strip()]

    try:
        chapter_index = int(chapter_id)
    except ValueError:
        return ""


    if chapter_index <= 1:
        previous_paragraphs = []  
    else:
        previous_paragraphs = paragraphs[: chapter_index - 1]

    return "\n\n".join(previous_paragraphs)

    


# previous attempt at character grid image generation for 'image' RAG (caused hallucinations)
""" def character_grid(columns,  images,space=20,labels=None, label_height=30, filename="character_grid.png"):
    
    if labels is None:
        labels = [os.path.splitext(os.path.basename(p))[0] for p in images]
    rows = len(images) // columns
    if len(images) % columns:
        rows += 1 
 
    opened_images = [Image.open(image) for image in images]
    width_max = max(img.width for img in opened_images)
    height_max = max(img.height for img in opened_images)

    tile_height = height_max + label_height

    background_width = width_max * columns + space * (columns - 1)
    background_height = tile_height * rows + space * (rows - 1)

    background = Image.new("RGBA",(background_width, background_height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("arial.ttf", 30)

    x = 0
    y = 0

    for i, (img, label) in enumerate(zip(opened_images, labels)):
        x_offset = int((width_max - img.width) / 2)
        y_offset = int((height_max - img.height) / 2)
        background.paste(img, (x + x_offset, y + y_offset))
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = x + (width_max - text_w) // 2
        text_y = y + height_max + (label_height - text_h) // 2
        draw.text((text_x, text_y), label, fill=(0, 0, 0, 255), font=font)
       
        x += width_max + space
        if (i + 1) % columns == 0:
            x = 0
            y += tile_height + space
    background= background.resize((1024,1024), Image.LANCZOS)
    characters_dir = os.path.join(settings.MEDIA_ROOT, "uploads", "characters")
    os.makedirs(characters_dir, exist_ok=True)

    save_path = os.path.join(characters_dir, filename)

    background.save(save_path)
 """