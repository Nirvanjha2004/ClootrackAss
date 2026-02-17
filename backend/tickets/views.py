from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q, Count, Min
from django.utils import timezone
from .models import Ticket
from .serializers import TicketSerializer
from .llm_service import LLMClassifier


class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Ticket CRUD operations.
    Provides list, create, and partial_update actions with filtering and search.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    
    def get_queryset(self):
        """
        Override get_queryset to handle query parameters for filtering and search.
        Supports: category, priority, status (exact filters) and search (title/description).
        """
        queryset = super().get_queryset()
        
        # Get query parameters
        category = self.request.query_params.get('category', None)
        priority = self.request.query_params.get('priority', None)
        status_filter = self.request.query_params.get('status', None)
        search = self.request.query_params.get('search', None)
        
        # Apply exact filters
        if category:
            queryset = queryset.filter(category=category)
        
        if priority:
            queryset = queryset.filter(priority=priority)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Apply search filter using Q objects for title and description
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        List all tickets ordered by newest first.
        Applies filters from query parameters via get_queryset().
        """
        queryset = self.get_queryset().order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new ticket.
        Returns 201 on success.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a ticket (PATCH request).
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


@api_view(['GET'])
def ticket_stats(request):
    """
    Return aggregated ticket statistics.
    Includes total count, open count, average per day, and breakdowns by priority and category.
    """
    # Total ticket count
    total_tickets = Ticket.objects.count()
    
    # Open ticket count
    open_tickets = Ticket.objects.filter(status='open').count()
    
    # Calculate average tickets per day
    earliest = Ticket.objects.aggregate(Min('created_at'))['created_at__min']
    if earliest:
        days = (timezone.now() - earliest).days + 1
        avg_per_day = total_tickets / days
    else:
        avg_per_day = 0
    
    # Priority breakdown using aggregation
    priority_breakdown = dict(
        Ticket.objects.values('priority')
        .annotate(count=Count('id'))
        .values_list('priority', 'count')
    )
    
    # Category breakdown using aggregation
    category_breakdown = dict(
        Ticket.objects.values('category')
        .annotate(count=Count('id'))
        .values_list('category', 'count')
    )
    
    return Response({
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'avg_tickets_per_day': round(avg_per_day, 1),
        'priority_breakdown': priority_breakdown,
        'category_breakdown': category_breakdown,
    })


@api_view(['POST'])
def classify_ticket(request):
    """
    Classify a ticket description using LLM.
    Returns suggested category and priority, or graceful fallback if LLM fails.
    """
    description = request.data.get('description', '')
    
    # Validate description is not empty
    if not description or not description.strip():
        return Response(
            {'error': 'Description is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Call LLM classifier
    classifier = LLMClassifier()
    result = classifier.classify_ticket(description)
    
    if result:
        return Response(result)
    else:
        # Graceful fallback when LLM is unavailable
        return Response(
            {
                'suggested_category': 'general',
                'suggested_priority': 'medium',
                'note': 'Using default values (LLM unavailable)'
            }
        )
