from django.db import models
from django.utils import timezone
from django.db.models import JSONField                 


class Book(models.Model):
    """
    Represents an uploaded EPUB and all derived/processed information for it.

    This model is the 'root' entity:
      - Chapters, Characters, and derived artifacts (metadata, relationships, etc.)
        are all attached to a Book.
    """
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)
    epub_file = models.FileField(upload_to='uploads/epubs/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    cover_image = models.ImageField(upload_to='uploads/covers/', null=True, blank=True)
    last_chapter_visited = models.IntegerField(default=1)
    # whole book summary
    summary = models.TextField(default='')
    #JSON object containing all metadat on book
    inferred_metadata =models.JSONField(default=dict, blank=True)
    #charcter relationship information
    relationships = models.JSONField(default=dict, blank=True)


    def __str__(self):
        return self.title



class Chapter(models.Model):
    """
    Represents one chapterextracted from the EPUB. A book has many chapters
    
    """

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)

    def __str__(self):
        return f"{self.book.title} - {self.title or f'Chapter {self.number}'}"
    
class Event(models.Model):
    """
    Represents an extracted event inside a chapter.A chaper has many events.Events ordered by
    uniue (chapter, number)
    """
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='events')
    number= models.PositiveIntegerField()
    start_index = models.PositiveIntegerField()
    summary = models.TextField(blank=True)
    label = models.TextField(blank=True)

    def __str__(self):
        return f"{self.chapter.book.title} - Ch {self.chapter.number} - Event {self.number}: {self.label}"
    
    class Meta:
        ordering = ['chapter', 'number']
        unique_together = ('chapter', 'number')

ROLE_CHOICES = (
    ("protagonist", "protagonist"),
    ("antagonist", "antagonist"),
    ("supporting character", "supporting character"),
)

class Character(models.Model):

    """
    Represents a character extracted from a book. A book has many characters

    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default="supporting character")
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=64, blank=True, default="")
    personality = models.TextField(blank=True, default="")
    appearance = models.TextField(blank=True, default="")
    bio = models.TextField(blank=True, default="")
    # Store chapter numbers where the character appears
    chapters_appeared = JSONField(default=list, blank=True)
    image = models.ImageField(upload_to='uploads/characters/', blank=True,null=True)

    class Meta:
        unique_together = ("book", "name")

    def __str__(self):
        return f"{self.name} ({self.book.title})"
