from rest_framework import routers
from django.urls import path
from .views import *

urlpatterns = [
    path('books/upload/', upload_epub, name='upload_epub'),
    path('books/', get_books, name='get_books'),
    path('books/<int:book_id>/chapters/', get_all_chapters, name='get_all_chapters'),
    path('books/<int:book_id>/chapters/<int:chapter_id>/', get_chapter),
    path('books/summary/<int:book_id>/<int:chapter_id>/', get_summary),
    path('books/<int:book_id>/last_chapter', get_last_chapter),
    path('books/<int:book_id>/set_last/<int:chapter_num>/', set_last_chapter),
    path('books/query/<int:book_id>/<str:query>/', query_book),
    path('books/<int:book_id>/characters/', get_characters ),
    path('books/<int:book_id>/chapters/<int:chapter_id>/scene/<int:event_number>/',get_scene),
    path("books/<int:book_id>/graph/", get_book_relationship_graph),

]

 

