import os
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Book,Chapter,Character
from ebooklib import epub
from bs4 import BeautifulSoup
import ebooklib
from django.utils.html import strip_tags
from .serializers import CharacterSerializer
from openai import OpenAI


# importing LLM modules
from books.llm_modules.summarizer import *
from books.llm_modules.RAGquery import *
from books.llm_modules.character_extractor import *
from books.llm_modules.image_gen import *
from books.llm_modules.Chroma_embed import *
from books.llm_modules.event_extractor import *
from books.llm_modules.metadata_extractor import *


# importing utility functions
from .utils import *



@api_view(['POST'])
def upload_epub(request):
    """
    POST /api/books/upload (example)

    Main frontend endpoint:
    1) Saves the uploaded EPUB as a Book row.
    2) Reads EPUB metadata (title/author) and stores it.
    3) Extracts a cover image (if found) into MEDIA/uploads/covers/.
    4) Extracts each document item as a Chapter (HTML content).
    5) Runs LLM modules :
       - summarize_all_chapters
       - get_book_metadata (tags, synopsis, MoodList, etc.)
       - character extraction + relationship extraction
       - event extraction + save to DB
       - load_book() to build / refresh vector embeddings for RAG
    6) Store generated information as book attributes
    Returns the created book id.

    """

    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    
     # Create Book row in DB
    book = Book.objects.create(title=file.name.replace('.epub', ''), epub_file=file)
    epub_book = epub.read_epub(book.epub_file.path)
    title = epub_book.get_metadata('DC', 'title')
    author = epub_book.get_metadata('DC', 'creator')
    book.title = title[0][0] if title else book.title
    book.author = author[0][0] if author else ''
    book.save()

    # Extract book cover image if possible
    for item in epub_book.get_items_of_type(ebooklib.ITEM_IMAGE):
        if 'cover' in item.get_name().lower():
            # save to MEDIA ROOT folder
            cover_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', 'covers')
            os.makedirs(cover_folder, exist_ok=True)

            cover_path = os.path.join(cover_folder, f'cover_{book.id}.jpg')
            with open(cover_path, 'wb') as f:
                f.write(item.get_content())

            book.cover_image = f'uploads/covers/cover_{book.id}.jpg'
            book.save()
            break

    # Extract chapters from all HTML/XHTML document items
    chapter_num = 1
    for item in epub_book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_body_content(), features="lxml")
        if soup is None:
            soup = BeautifulSoup(item.get_body_content(), "html.parser")


        for tag in soup(["script", "style"]):
            tag.decompose()

        body = soup.body
        content_html = "".join(str(child) for child in body.contents) if body else str(soup)

        
        title_tag = soup.find(["h1", "h2"])
        chapter_title = title_tag.get_text(strip=True) if title_tag else f"Chapter {chapter_num}"

        #create chapter objects in DB
        Chapter.objects.create(
            book=book,
            number=chapter_num,
            title=chapter_title,
            content=content_html,  
        )
        chapter_num += 1
        
    #LLM call to text summarizer module    
    book.summary=summarize_all_chapters(book.id)
    book.save()
    #LLM call to metadata extractor module  
    book.inferred_metadata=get_book_metadata(book.id).model_dump()
    book.save()

    #LLM call to character extractor module  
    result = set_characters(book.id)  
    
    # save character objects to DB   
    if isinstance(result, CharacterList):
            save_characters_to_db(book, result)
            character_names = [c.name for c in result.Characters]
    else:
            character_names = []
    
    #LLM call to character extractor module (extract relationships) 
    book.relationships = set_character_relationships(book.id).model_dump()
    book.save()

    #character_grid(3,[c.image.path for c in Character.objects.filter(book=book) if c.image])

    #LLM call to character extractor module (extract relationships) 
    all_events= extract_events(book.id)
    save_events_to_db(book, all_events)

    #Build embeddings for RAG querying (Chroma)
    load_book(book.id) 


    return Response(
            {
                "message": "Book uploaded successfully",
                "book_id": book.id,          
            },
            status=status.HTTP_201_CREATED
        )
            

@api_view(['GET'])
def get_books(request):
    """
    GET /api/books/

    Returns a list of book attritutes for homescreen display 
    Includes:
      - basic Book fields
      - absolute cover image URL for the frontend
      - inferred tags + synopsis (with fallbacks if metadata missing)
    """

    books = Book.objects.all()
    data = []
    for book in books:
        inferred = book.inferred_metadata or {}
        data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'created_at': book.created_at,
            'cover_image': request.build_absolute_uri(book.cover_image.url) if book.cover_image else None,
            'tags':inferred.get("main_genre") or ["Adventure","Historical"],
            'synopsis':inferred.get("synopsis") or "Summary TBD",
        })
    return Response(data)

#endpoint testing
@api_view(['GET'])
def get_all_chapters(request, book_id):
    chapters = Chapter.objects.filter(book_id=book_id).values('number', 'title', 'content')
    return Response(list(chapters))


@api_view(['GET'])
def get_chapter(request, book_id, chapter_id):
    """
    GET /api/books/<book_id>/chapters/<chapter_number>/

    Returns a single chapter plus book header info and a “music mood” field
    taken from inferred_metadata['MoodList'][chapter_id]['mood'].
    """

    try:
        chapter = Chapter.objects.select_related('book').get(book_id=book_id, number=chapter_id)
    except Chapter.DoesNotExist:
        return Response({'error': 'Chapter not found'}, status=status.HTTP_404_NOT_FOUND)

    book = chapter.book

    try:
        # Mood lookup for chapter.defaults to "dark" if missing
        music=book.inferred_metadata['MoodList'][chapter_id]['mood']
    except Exception as e:
        print("Error while getting music:", repr(e)) 
        music = "dark"

    return Response({
        'id': book.id,
        'title': book.title,          
        'author': book.author,       
        'chapter_number': chapter.number,
        'chapter_title': chapter.title,
        'content': chapter.content, 
        'music':music, 
    })



@api_view(['POST'])
def set_last_chapter(request, book_id, chapter_num):
    """
    POST /api/books/<book_id>/last_chapter/<chapter_num>/

    sets pointer to last chapter read.
    """
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

    book.last_chapter_visited = chapter_num
    book.save()
    return Response({'message': f'Last chapter set to {chapter_num} for {book.title}'}, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_last_chapter(request, book_id):
    """
    GET /api/books/<book_id>/last_chapter/

    Returns the last chapter read
    """

    try:
        book = Book.objects.get(id=book_id)
        chapter = Chapter.objects.get(book=book, number=book.last_chapter_visited)
    except (Book.DoesNotExist, Chapter.DoesNotExist):
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'chapter_number': chapter.number,
        'chapter_title': chapter.title,
        'content': chapter.content,
    })


@api_view(['GET'])
def get_summary(request,book_id, chapter_id):
    """
    GET /api/books/summary/<int:book_id>/<int:chapter_id>/

    Returns summary of book chapters so far.
    """
    return Response(
        {
            "summary": get_chapter_summary(book_id,chapter_id)
    ,
        },
        status=status.HTTP_200_OK,
    )
   
@api_view(["GET"])
def get_book_relationship_graph(request, book_id):
    """
    GET /api/books/<int:book_id>/graph/

    Converts stored relationship data into a graph structure:
      - nodes: [{id, label}]
      - edges: [{id, source, target, label}]
    For frontend graph visualization library format.
    """
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
    rlist = (book.relationships or {}).get("relationships", [])

    names = set()
    for r in rlist:
        s = r.get("source")
        t = r.get("target")
        if s: names.add(s)
        if t: names.add(t)

    nodes = [{"id": n, "label": n} for n in sorted(names)]

    edges = []
    for i, r in enumerate(rlist):
        s, t = r.get("source"), r.get("target")
        if not s or not t:
            continue
        edges.append({
            "id": f"{s}-{t}-{i}",
            "source": s,
            "target": t,
            "label": r.get("label", ""),
        })

    return Response({"nodes": nodes, "edges": edges}, status=status.HTTP_200_OK)

    

@api_view(['GET'])
def get_scene(request,book_id,chapter_id,event_number):
    """
    GET /api/books/<int:book_id>/chapters/<int:chapter_id>/scene/<int:event_number>/

    Generates (or retrieves cached) scene image for a given event.
    Response contains:
      - image_url (absolute)
      - caption (event label)
    """

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        chapter = Chapter.objects.select_related('book').get(book_id=book_id, number=chapter_id)
    except Chapter.DoesNotExist:
        return Response({'error': 'Chapter not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        event = Event.objects.get(chapter=chapter, number=event_number)

    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    
    sceneURL=generate_or_get_scene_image(book_id,chapter_id,event_number)
    data={
            'image_url': request.build_absolute_uri(sceneURL),
            'caption': event.label,               
        }
    return Response(data)

@api_view(['GET'])
def query_book(request,book_id,query):  
    """
    GET /api/books/query/<int:book_id>/<str:query>/

    Runs RAG/LLM question answering over the book`s content.
    LLM call to RAG query module.
    """
    
    return Response({"answer": LLMquery(book_id,query)}
        
    )

@api_view(['GET'])
def get_characters(request, book_id=None):

    """
    GET /api/books/<book_id>/characters/
    Returns all extracted characters for a book using CharacterSerializer.
    """

    characters = Character.objects.filter(book_id=book_id)
    serializer = CharacterSerializer(characters, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)