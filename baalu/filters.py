from django_filters import FilterSet, filters
from .models import *



class BookFilter(FilterSet):
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    class Meta:
        model = Books
        fields = {
            'category': ['exact'],  # ?category=1
            'bestseller': ['exact'],  # ?bestseller=true
            'v_nalich': ['exact'],  # ?v_nalich=БИШКЕК
            'pereplet': ['exact'],  # ?pereplet=Твердый переплет
            'god_izdaniya': ['exact'],  # ?god_izdaniya=2023
        }