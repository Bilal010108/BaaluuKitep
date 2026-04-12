from .models import Books, Store, Category, Reklama
from modeltranslation.translator import TranslationOptions,register


@register(Store)
class StoreTranslationOptions(TranslationOptions):
    fields = ('store_name', 'store_description')


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('category_name', )


@register(Books)
class BooksTranslationOptions(TranslationOptions):
    fields = ('books_name','description',)


@register(Reklama)
class ReklamaTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
