"""
Contacts views - ViewSets for Tag, Company, Contact, ContactGroup, CustomFieldDefinition, Note.
"""
import csv
from io import StringIO

from django.http import HttpResponse
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.contacts.models import (
    Tag,
    Company,
    Contact,
    ContactGroup,
    CustomFieldDefinition,
    Note,
)
from apps.contacts.serializers import (
    TagSerializer,
    CompanySerializer,
    CompanyListSerializer,
    ContactSerializer,
    ContactListSerializer,
    ContactGroupSerializer,
    CustomFieldDefinitionSerializer,
    NoteSerializer,
    ContactImportSerializer,
)
from apps.contacts.filters import ContactFilter, CompanyFilter


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for Tag CRUD operations."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'category']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Company CRUD operations."""
    queryset = Company.objects.select_related('owner').all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_class = CompanyFilter
    search_fields = ['name', 'domain', 'industry']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return CompanyListSerializer
        return CompanySerializer


class ContactViewSet(viewsets.ModelViewSet):
    """ViewSet for Contact CRUD operations with import/export."""
    queryset = Contact.objects.select_related('company', 'owner').prefetch_related('tags').all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_class = ContactFilter
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'email', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return ContactListSerializer
        return ContactSerializer

    @action(detail=True, methods=['post'])
    def add_tags(self, request, pk=None):
        """Add tags to contact."""
        contact = self.get_object()
        tag_ids = request.data.get('tag_ids', [])

        if not isinstance(tag_ids, list):
            return Response(
                {'error': 'tag_ids must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tags = Tag.objects.filter(id__in=tag_ids)
        contact.tags.add(*tags)

        serializer = self.get_serializer(contact)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_tags(self, request, pk=None):
        """Remove tags from contact."""
        contact = self.get_object()
        tag_ids = request.data.get('tag_ids', [])

        if not isinstance(tag_ids, list):
            return Response(
                {'error': 'tag_ids must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tags = Tag.objects.filter(id__in=tag_ids)
        contact.tags.remove(*tags)

        serializer = self.get_serializer(contact)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def import_contacts(self, request):
        """Import contacts from CSV file."""
        serializer = ContactImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        csv_file = serializer.validated_data['file']
        has_header = serializer.validated_data['has_header']

        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(StringIO(decoded_file))

            created_count = 0
            errors = []

            with transaction.atomic():
                for row_num, row in enumerate(csv_data, start=1):
                    if row_num == 1 and not has_header:
                        continue

                    try:
                        # Extract required fields
                        name = row.get('name', '').strip()
                        email = row.get('email', '').strip()

                        if not name or not email:
                            errors.append(f"Row {row_num}: Missing name or email")
                            continue

                        # Check if contact already exists
                        if Contact.objects.filter(email=email).exists():
                            errors.append(f"Row {row_num}: Email {email} already exists")
                            continue

                        # Create contact
                        contact = Contact.objects.create(
                            name=name,
                            email=email,
                            phone=row.get('phone', '').strip(),
                            status=row.get('status', Contact.Status.ACTIVE),
                            source=Contact.Source.IMPORT,
                            owner=request.user
                        )
                        created_count += 1

                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")

            return Response({
                'created': created_count,
                'errors': errors
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Failed to process CSV: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def export_contacts(self, request):
        """Export contacts to CSV file."""
        contacts = self.filter_queryset(self.get_queryset())

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contacts.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Phone', 'Status', 'Source', 'Company', 'Created At'])

        for contact in contacts:
            writer.writerow([
                contact.name,
                contact.email,
                contact.phone,
                contact.status,
                contact.source,
                contact.company.name if contact.company else '',
                contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response


class ContactGroupViewSet(viewsets.ModelViewSet):
    """ViewSet for ContactGroup CRUD operations."""
    queryset = ContactGroup.objects.prefetch_related('contacts').all()
    serializer_class = ContactGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=['post'])
    def add_contacts(self, request, pk=None):
        """Add contacts to group."""
        group = self.get_object()

        if group.is_dynamic:
            return Response(
                {'error': 'Cannot manually add contacts to dynamic group'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contact_ids = request.data.get('contact_ids', [])

        if not isinstance(contact_ids, list):
            return Response(
                {'error': 'contact_ids must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contacts = Contact.objects.filter(id__in=contact_ids)
        group.contacts.add(*contacts)

        serializer = self.get_serializer(group)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_contacts(self, request, pk=None):
        """Remove contacts from group."""
        group = self.get_object()

        if group.is_dynamic:
            return Response(
                {'error': 'Cannot manually remove contacts from dynamic group'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contact_ids = request.data.get('contact_ids', [])

        if not isinstance(contact_ids, list):
            return Response(
                {'error': 'contact_ids must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contacts = Contact.objects.filter(id__in=contact_ids)
        group.contacts.remove(*contacts)

        serializer = self.get_serializer(group)
        return Response(serializer.data)


class CustomFieldDefinitionViewSet(viewsets.ModelViewSet):
    """ViewSet for CustomFieldDefinition CRUD operations."""
    queryset = CustomFieldDefinition.objects.all()
    serializer_class = CustomFieldDefinitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entity_type', 'field_type']


class NoteViewSet(viewsets.ModelViewSet):
    """ViewSet for Note CRUD operations."""
    queryset = Note.objects.select_related('contact', 'author').all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact']

    def perform_create(self, serializer):
        """Auto-set author on creation."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """Toggle note pin status."""
        note = self.get_object()
        note.pinned = not note.pinned
        note.save(update_fields=['pinned'])

        serializer = self.get_serializer(note)
        return Response(serializer.data)
