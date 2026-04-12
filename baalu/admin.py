from django.contrib import admin
from .models import *
from modeltranslation.admin import TranslationAdmin
from .translations import *


class BookImageInline(admin.TabularInline):
    model = BookImages
    extra = 1


@admin.register(Books)
class BooksAdmin(TranslationAdmin):
    inlines = [BookImageInline]
    list_display = ['books_name', 'position', 'category', 'price',]
    list_editable = ['position','category','price']
    list_filter = ['category',]
    search_fields = ['books_name', 'author', 'isbn', 'artikul']
    list_per_page = 20
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Store)
class StoreAdmin(TranslationAdmin):
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }



@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at','phone_number','address']
    list_editable = ['status',]
    list_filter = ['status']
    search_fields = ['user__username', 'phone_number', 'address']
    list_per_page = 20


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'books', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['user__username', 'books__books_name']
    list_per_page = 20

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'is_used', 'used_by', 'created_at']
    list_editable = ['is_used','discount_percent']
    list_filter = ['is_used']
    search_fields = ['code']
    list_per_page = 20

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['books', 'discount_percent', 'is_active', 'start_date', 'end_date']
    list_filter = ['is_active']
    list_editable = ['is_active','discount_percent','start_date','end_date']
    list_per_page = 20

admin.site.register(UserProfile)
admin.site.register(Reklama)
admin.site.register(Favorite)
admin.site.register(FavoriteBook)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(CommentLike)
admin.site.register(Payment)




