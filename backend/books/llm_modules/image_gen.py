import base64
from django.core.files.base import ContentFile
from openai import OpenAI
import base64
from django.conf import settings
import os
from ..models import *
from ..utils import get_chapter_summary
from django.utils.html import strip_tags
import traceback
import re


def generate_character_image(character, use_default=False):
    """
    Generate  a portrait image for a Character model object.

    If use_default = True :
         - loads a local file default_character.jpg from MEDIA/uploads/characters/
         - saves it into character.image without calling the LLM API
        Used to save cost when testing other feaures

    If use_default = False :
         - Creates a text prompt describing a character`s appearance using Character object fields (name, role, appearance, personality) 
         - calls LLM image generation API using text prompt
         - saves the image into character.image (stored under uploads/characters/)

    Returns:
      - True if the image was saved successfully
      - False if anything failed
    """
    try:
        # If user chooses default image, skip API call 
        if use_default:
            default_path = os.path.join(
    settings.MEDIA_ROOT, "uploads", "characters", "default_character.jpg"
)
            if not os.path.exists(default_path):
                raise FileNotFoundError("Default character image not found")

            with open(default_path, "rb") as f:
                character.image.save(
                    f"default_{character.name.replace(' ', '_')}.jpg",
                    ContentFile(f.read()),
                    save=True
                )

            print(f"Default image used for {character.name}")
            return True

        # image generation part
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        client = OpenAI(api_key=api_key)

        # text description prompt also includes a consistent art style to ensure character style consistency in descriptions.Future implementations to allow custom style
        prompt = ("Your role is to generate the portrait of a fictional character from a book. Details about the character are provided below."
        " Use these details to generate image:"
            f"Portrait of {character.name}, "
            f"{character.gender or 'unspecified gender'}, "
            f"role: {character.role or 'unspecified role'}. "
            f"Physical appearance: {character.appearance or 'unspecified appearance'}. "
            f"Personality: {character.personality or 'unspecified personality'}. "
            f"Art style of generated image: detailed fantasy storybook illustration, warm lighting, expressive portrait."
        )

        #Image generation API call
        result = client.images.generate(
            model="gpt-image-1-mini",
            prompt=prompt,
            size="1024x1024",
            quality="medium",
            n=1,
        )

        image_base64 = result.data[0].b64_json
        if not image_base64:
            raise ValueError("No image data returned from image model")

        image_bytes = base64.b64decode(image_base64)
        name=re.sub(r'[\\/:"*?<>|]+', '_', character.name)
        filename = f"{name.replace(' ', '_')}.png"

        #Save into ImageField (folder is media/uploads/characters/)
        character.image.save(filename, ContentFile(image_bytes), save=True)
        print(f"AI image generated for {character.name}")
        return True

    except Exception as e:
        print(f"Failed to generate image for {character.name}: {e}")
        return False



def generate_or_get_scene_image(book_id,chapter_id,event_number):
    """
    Generate (or load cached) a scene image for a specific event in a chapter.

    - scene images are stored on disk under MEDIA/uploads/scenes/
    - filename convention: scene_<book_id>_<chapter_id>_<event_number>.png
    - if the file already exists, return the MEDIA_URL path immediately

    - OTHERWISE, call scene description API to generate a text description of scene/event.Text description is then passed as input prompt to Image generation API.

    """


    scenes_folder = os.path.join(settings.MEDIA_ROOT, "uploads", "scenes")
    os.makedirs(scenes_folder, exist_ok=True)

    filename = f"scene_{book_id}_{chapter_id}_{event_number}.png"
    filepath = os.path.join(scenes_folder, filename)

    
    if os.path.exists(filepath):
        return f"{settings.MEDIA_URL}uploads/scenes/{filename}"
    else:

        try:
            image_prompt=""

            #uses book,chapter and event objects to generate text description of scene
            image_prompt=get_scene_description(book_id,chapter_id,event_number)

            client = OpenAI()
            result = client.images.generate(
            model="gpt-image-1",
            n=1,
            quality="medium",
            size="1024x1024",
            prompt=image_prompt) 
 
            #save image to disk (folder is media/uploads/scenes/)
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            save_dir = os.path.join(settings.MEDIA_ROOT, "uploads", "scenes")
            os.makedirs(save_dir, exist_ok=True)

            filename = f"scene_{book_id}_{chapter_id}_{event_number}.png"
            save_path = os.path.join(save_dir, filename)

            with open(save_path, "wb") as f:
                f.write(image_bytes)
            return f"{settings.MEDIA_URL}uploads/scenes/{filename}"

        except Exception as e:
            print("[SCENE IMAGE] Error while generating scene image:", repr(e))
            traceback.print_exc()  
            #default image fallback
            return f"{settings.MEDIA_URL}uploads/characters/default_character.jpg"





def get_scene_description(book_id,chapter_id,event_number):
    """
    Create a detailed text prompt for scene image generation for a given event using the following information:
      - Book inferred metadata: main_genre, time_period, primary_setting
      - Event label + Event summary
      - Truncated book summary upto current chapter (Context 1)
      - Character list (Context 2) to include names/details when relevant
      - extract full event text based on markers 


    Returns:
      - response.output_text (the image prompt), as plain text
    """
    #book info
    book = Book.objects.get(id=book_id)
    genre=book.inferred_metadata['main_genre']
    time_period=book.inferred_metadata['time_period']
    setting=book.inferred_metadata['primary_setting']

    #chapter info
    chapter = Chapter.objects.get(book_id=book_id, number=chapter_id)
    full_chapter= strip_tags(chapter.content)
    # extracts the full text of event in chapter using previously set event markers to get substring
    if event_number==1:
        start_idx = full_chapter.find('PLACEHOLDER FOR IMAGE 1')
        event_details = full_chapter[:start_idx]
    else:
        start=f'PLACEHOLDER FOR IMAGE {event_number-1}'
        end=f'PLACEHOLDER FOR IMAGE {event_number}'
        start_idx = full_chapter.find(start)
        end_idx=full_chapter.find(end)
        event_details =full_chapter[start_idx + len(start):end_idx]

    #full book summary upto chapter
    context_1= get_chapter_summary(book_id,chapter_id+1)

    #list of character info, including description of appearance
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

    event =Event.objects.get(chapter=chapter, number=event_number) 


    #everything that was extracted passed to this prompt
    client=OpenAI()
    response = client.responses.parse(
    model="gpt-4.1-nano",
    input=[
        {"role": "system",
          f"content": "You are an expert prompt engineer.Your role is to write a text prompt which will be used as input to an image generation model.The text prompt describes a scene from a chapter of a book called {book.title}. You have been given the part of the chapter where event occurs along with a short description of event. You should generate a prompt for an image generation model that describes  a scene using this event information. You should be descriptive as possible with characters,background and actions since the image generation will only have your prompt and no information on the book.You should only use information currently provided  for generation.You have also been provided extra context information that are only there to give you more context about the event information. CONTEXT 1 is a chapter by chapter summary of book, with the last paragraph being the chapter where the event occurs.CONTEXT 2 is a list of 10 major characters in the book. If a character from list is present in the event, include their name. You should only output the image generation prompt and nothing else. The art style should be: 'detailed fantasy storybook illustration, warm lighting, expressive' "},
        {
            "role": "user",
            "content": f"Here are the event details :\n\n"
            "MAIN EVENT INFORMATION FOR GENERATION:\n"
            f"Event label: {event.label}"
            f"Event synopsis: {event.summary}"
            f"Event extract from book:\n\n{event_details}\n\n"
            f"Book setting:\n\nThe book events occur primarily in the {time_period} time period. The primary setting of the book is {setting} and the main genres of the book are {genre}\n\n"
            "EXTRA CONTEXT FOR MAIN EVENT INFORMATION:\n"
            f"CONTEXT 1:\n{context_1}\n\n"
            f"CONTEXT 2:\n{context_2}\n\n"
            "PROMPT FOR IMAGE GENERATION:\n\n",

        },]
        )
    #print("''''''''''''''''''''''''")
    #print(response.output_text)
    
    #text description of event
    return response.output_text



