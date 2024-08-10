from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models.aggregates import Count
from django.http import HttpRequest
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models

# Register your models here.

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin) -> list[tuple[Any, str]]:
        return [
            ('<10', 'LOW')
        ]
    
    def queryset(self, request: Any, queryset: QuerySet[models.Product]) -> QuerySet[Any] | None:
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_filter = ['collection', 'last_update', InventoryFilter]
    prepopulated_fields = {
        'slug' : ['title']
    }
    exclude = ['promotions']
    
    def collection_title(self, product: models.Product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product: models.Product):
        if product.inventory < 10:
            return 'LOW'
        return 'OK'

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_count']
    list_per_page = 20

    @admin.display(ordering='product_count')
    def product_count(self, collection: models.Collection):
        return collection.product_count
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            product_count=Count('product')
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders')
    def orders(self, customer: models.Customer):
        url = (reverse('admin:store_order_changelist')
               + '?'
               + urlencode({
                   'customer__id': str(customer.id)
               }) 
            )
        return format_html('<a href={}>{}</a>', url, customer.orders)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            orders=Count('order')
        )

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer_name',]
    list_per_page = 20
    list_select_related = ['customer']
    ordering = ['id']
    autocomplete_fields = ['customer']

    def customer_name(self, order: models.Order):
        url = (reverse('admin:store_customer_changelist') 
               + '?'
               + urlencode({
                   'id': str(order.customer.id)
               })
            )
        anchor = format_html('<a href={}>{}</a>', url, order.customer.first_name)
        return anchor