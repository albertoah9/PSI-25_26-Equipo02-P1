from django.contrib import admin

from .models import Author, Genre, Book, BookInstance, Language

# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)
admin.site.register(Language)

# Clase BookInline para meter Book dentro de Author
class BookInline(admin.TabularInline):
    model = Book
    extra = 0

# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'date_of_death') # como se muestra
    
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')] # cuando se rellenan los campos
    
    inlines = [BookInline]

admin.site.register(Author, AuthorAdmin) # Register the admin class with the associated model

# Clase BookInstanceInline para meter Book Instance dentro de Book
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')

    inlines = [BooksInstanceInline]

# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_back', 'id')
    
    list_filter = ('status', 'due_back', 'book')
    
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }), 
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )


