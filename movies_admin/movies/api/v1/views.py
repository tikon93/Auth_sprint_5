from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies.models import BaseFilmwork, Genre, Person

import logging
logger = logging.getLogger(__name__)


class MoviesApiMixin:
    model = BaseFilmwork
    http_method_names = ['get']

    def get_queryset(self):

        query_filters: dict = self.request.GET
        query_set = self.model.objects.all()
        if (genre := query_filters.get("genre")) is not None:
            genre = get_object_or_404(Genre, name=genre)
            query_set = query_set.filter(genres=genre)

        if (person_name := query_filters.get("person_name")) is not None:
            person = get_object_or_404(Person, full_name=person_name)
            query_set = query_set.filter(persons=person)

        if (title := query_filters.get("title")) is not None:
            query_set = query_set.filter(title=title)

        return query_set.prefetch_related('genres', 'persons',
                                          Prefetch('personrole_set', to_attr='roles')).order_by('created')

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):

    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, page, queryset, is_paginated = self.paginate_queryset(self.object_list, self.paginate_by)
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "results": [m.as_dict() for m in queryset]
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        return kwargs["object"].as_dict()
