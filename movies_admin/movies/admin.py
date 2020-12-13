from django.contrib import admin

from .models import Movie, Series, PersonRole, Person, Genre, GenreMovie, FilmworkType


class PersonRoleInline(admin.TabularInline):
    model = PersonRole
    extra = 0


class GenreMovieInline(admin.TabularInline):
    model = GenreMovie
    extra = 0


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', )
    fields = ('name', 'description')
    search_fields = ('name', 'description')
    inlines = [
        GenreMovieInline
    ]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', )
    fields = ('full_name', 'birth_date')
    inlines = [
        PersonRoleInline
    ]


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'creation_date', 'rating', 'id')
    fields = (
        'title', 'description', 'creation_date', 'certificate',
        'file_path', 'rating', 'age_lower_limit'
    )
    search_fields = ('title', 'description', 'id')
    inlines = [
        PersonRoleInline, GenreMovieInline
    ]
    list_filter = ('genres__name', )

    def get_queryset(self, request):
        query = super().get_queryset(request)
        filtered_query = query.filter(type=FilmworkType.MOVIE)
        return filtered_query


@admin.register(Series)
class SeriesAdmin(MovieAdmin):
    """
    According to initial task Series must have different set of fields than Movie. In fact, Series and Movies utilize
    the same table and differs only by type. There is no strict limitations to fill series-specific fields for movie
    but it will make no affect.
    """
    fields = (
        'title', 'description', 'creation_date', 'production_end_date', 'certificate',
        'file_path', 'rating',
    )

    def get_queryset(self, request):
        query = super().get_queryset(request)  # we have to get original, not filtered query set
        filtered_query = query.filter(type=FilmworkType.SERIES)
        return filtered_query
