import json
from django.core.cache import cache
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.metadata import BaseMetadata
from rest_framework.response import Response
from .serializers import BackendSerializer


class BulkActivateEndpointMetadata(BaseMetadata):
    def determine_metadata(self, request, view):
        return {
            "name": "Bulk activate",
            "description": "This will activate all backends in bulk based on user input (id_list). " +
                           "It will deactivate all other backends. " +
                           "WARNING: If you provide valid input with IDs that don't exist, the system will try to " +
                           "activate those and it will deactivate all other. This will result in all backends being " +
                           "deactivated.",
            "renders": [
                "application/json",
                "text/html"
            ],
            "parses": [
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data"
            ],
            "actions": {
                "POST": {
                    "id_list": {
                        "type": "list<int>",
                        "required": True,
                        "read_only": False,
                        "label": "ID list"
                    }
                }
            }
        }


class BackendViewSet(viewsets.ModelViewSet):
    serializer_class = BackendSerializer
    queryset = BackendSerializer.Meta.model.objects.all()

    @method_decorator(cache_page(60 * 60 * 24, key_prefix='backends'))  # cache view for 24 hours (or until invalidated)
    def list(self, request):
        """
        List all backends that a re currently active
        """
        queryset = self.queryset.filter(is_active=True)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def show_all(self, request):
        """
        Get all backends (bot active and disabled)
        """
        return Response(self.serializer_class(self.queryset.all(), many=True).data)

    @action(detail=False, methods=['post', 'options'])
    def bulk_activate(self, request):
        """
        This will activate all backends in bulk based on user input. It will deactivate all other backends.
        WARNING: If you provide valid input with IDs that don't exist, the system will try to activate those
        and it will deactivate all other. This will result in all backends being deactivated.
        """
        if request.method == 'OPTIONS':
            meta = BulkActivateEndpointMetadata()
            data = meta.determine_metadata(request, self)
            return Response(data)
        else:
            id_list = request.POST.get('id_list')
            if not id_list:
                raise ValidationError('You must provide a list of IDs.')
            try:
                id_list = json.loads(id_list)
                assert hasattr(id_list, '__iter__')
            except:
                raise ValidationError('id_list must be convertable to a list/array of integers.')
            model = self.serializer_class.Meta.model
            with transaction.atomic():
                model.objects.filter(pk__in=id_list).update(is_active=True)
                model.objects.exclude(pk__in=id_list).update(is_active=False)
                cache.delete_pattern('*backends*')
            return Response('OK')
