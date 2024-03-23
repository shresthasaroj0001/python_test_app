from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]
    
    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail" />')
        return ''
# This says ProductAdmin is the model of model Product
# admin.site.register(models.Product) is not required
# admin.site.unregister(models.Product)
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug':['title']
    }
    exclude = ['promotions']
    search_fields = ['title'] #used by autocomplete

    actions = ['clear_inventory']
    list_display = ['title', 'unit_price', 'invertory_status', 'collection_title']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 20
    list_select_related = ['collection']
    inlines = [ProductImageInline]

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def invertory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'
    
    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.',
            messages.ERROR
        )
    
    class Media:
        css = {
            'all':['store/styles.css']
        }

#Django modelAdmin search in google for more option

#admin.site.register(models.Collection)
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']
    search_fields = ['title'] #used by autocomplete   

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        # reverse('admin:app_model_page')
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'collection__id':str(collection.id)
            }))
        return format_html('<a href="{}">{}</a>', url, collection.products_count)
    
    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )

class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem 
    extra = 0

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at','customer']

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders']
    list_editable = ['membership']
    list_per_page = 20
    list_select_related=['user']
    ordering = ['user__first_name','user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders_count')
    def orders(self, order):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id':str(order.id)
            })) 
        return format_html('<a href="{}">{} count</a>', url, order.orders_count)
    
    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )
