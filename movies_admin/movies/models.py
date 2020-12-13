import datetime
import logging
import uuid
from typing import Dict

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


logger = logging.getLogger(__name__)


def now():
    return datetime.datetime.now(datetime.timezone.utc)


class Genre(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('название жанра'), max_length=255, null=False, unique=True)
    description = models.TextField(_('описание жанра'), blank=True, null=True)

    class Meta:
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')
        db_table = "content\".\"genre"

    def __str__(self):
        return self.name


class PossibleRoles(models.TextChoices):
    DIRECTOR = 'director', _('режиссёр')
    ACTOR = 'actor', _('актёр')
    WRITER = 'writer', _('сценарист')


class Person(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(_('имя'), max_length=255)
    birth_date = models.DateField(_('дата рождения'), blank=True, null=True)

    class Meta:
        verbose_name = _('участник')
        verbose_name_plural = _('участники')
        db_table = "content\".\"person"

    def __str__(self):
        return self.full_name


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    SERIES = 'series', _('сериал')


class BaseFilmwork(TimeStampedModel):
    """
    Main Filmwork model which describes all of possible fields - doesn't matter for series or for movie.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('название фильма'), max_length=255)
    description = models.TextField(_('описание фильма'), blank=True, null=True)
    creation_date = models.DateField(_('дата создания'), blank=True, null=True)
    certificate = models.TextField(_('сертификат'), blank=True, null=True)
    file_path = models.FileField(_('файл'), upload_to='film_works/', blank=True, null=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], blank=True, null=True)
    type = models.CharField(_('тип фильма'), max_length=20, choices=FilmworkType.choices)
    genres = models.ManyToManyField(Genre, blank=True, through='GenreMovie')
    persons = models.ManyToManyField(Person, blank=True, through='PersonRole')
    age_lower_limit = models.IntegerField(_('возрастной ценз'), validators=[MinValueValidator(0)], blank=True,
                                          null=True)
    production_end_date = models.DateField(_('дата окончания проекта'), blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content\".\"film_work"

    def _find_person_by_role(self, role) -> Person:
        for person in self.persons.all():
            if person.id == role.person_id:
                return person

        raise ValueError("Related person not found!")

    def as_dict(self) -> Dict:
        writers = []
        actors = []
        directors = []
        for role in self.roles:  # type: PersonRole
            person = self._find_person_by_role(role)
            if role.role == PossibleRoles.ACTOR:
                actors.append(person.full_name)
            elif role.role == PossibleRoles.WRITER:
                writers.append(person.full_name)
            elif role.role == PossibleRoles.DIRECTOR:
                directors.append(person.full_name)
            else:
                raise ValueError(f"Invalid role {role}")

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "creation_date": self.creation_date.strftime("%Y-%m-%d") if self.creation_date is not None else None,
            "rating": self.rating,
            "type": self.type,
            "genres": [g.name for g in self.genres.all()],
            "actors": actors,
            "directors": directors,
            "writers": writers
        }


class Movie(BaseFilmwork):
    """
    Just a proxy model to set default type=MOVIE and map to separate category  in admin panel
    """

    class Meta:
        proxy = True
        verbose_name = _('фильм')
        verbose_name_plural = _('фильмы')

    def save(self, *args, **kwargs):
        self.type = FilmworkType.MOVIE
        return super(Movie, self).save(*args, **kwargs)


class Series(BaseFilmwork):
    """
    Just a proxy model to set default type=MOVIE and map to separate category in admin panel
    """

    class Meta:
        proxy = True
        verbose_name = _('сериал')
        verbose_name_plural = _('сериалы')

    def save(self, *args, **kwargs):
        self.type = FilmworkType.SERIES
        return super(Series, self).save(*args, **kwargs)

    def clean(self):
        """
        Provides additional validation for involved dates
        """
        if self.creation_date is None and self.production_end_date is not None:
            raise ValidationError(_("Дата начала съёмок должна быть указана, если указана дата окончания"))


class PersonRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(_('роль'), max_length=30, choices=PossibleRoles.choices)
    film_work = models.ForeignKey(BaseFilmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created = models.DateField(_('дата создания роли'), blank=True, editable=False, default=now)

    class Meta:
        db_table = "content\".\"person_film_work"
        unique_together = (('role', 'film_work', 'person'),)


class GenreMovie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey(BaseFilmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created = models.DateField(_('дата создания роли'), blank=True, editable=False, default=now)

    class Meta:
        db_table = "content\".\"genre_film_work"
        unique_together = (('genre', 'film_work'),)
