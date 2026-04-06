from django.urls import path, include
from rest_framework import routers
from .models import *
from .views import *



routers = routers.SimpleRouter()

urlpatterns = [
    path('', include(routers.urls)),
    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),
    path('change_password/', change_password, name='change_password'),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # ✅ ДОБАВИЛИ профиль
    path('profile/', ProfileView.as_view(), name='profile'),

    path('clients/',ClientAPIView.as_view(),name='clients'),
    path('seller/',SellerAPIView.as_view(),name='seller'),

    path('store/',StoreListAPIView.as_view(),name='store_list'),
    path('store/<int:pk>/', StoreDetailAPIView.as_view(), name='store_detail'),
    path('store_create/',StoreListCreateAPIView.as_view(),name='store_create'),

    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('category_create/', CategoryCreateAPIView.as_view(), name='category-create'),


    path('books/', BooksListAPIView.as_view(), name='product-list'),
    path('books_create/', BooksCreateAPIView.as_view(), name='product-create'),
    path('books/<int:pk>/', BooksDetailAPIView.as_view(), name='product-detail'),

    path('bookimage/', BookImageListAPIView.as_view(), name='bookimage_image-create'),
    path('bookimage/<int:pk>/', BookImageDetailAPIView.as_view(), name='bookimage_image-detail'),

    path('sales/', SaleList.as_view(), name='sale-list'),
    path('sales/create/', SaleCreateAPIView.as_view(), name='sale-create'),
    path('sales/<int:pk>/', SaleDetail.as_view(), name='sale-detail'),

    path('reklama/', ReklamaList.as_view(), name='reklama-list'),
    path('reklama/create/', ReklamaCreate.as_view(), name='reklama-create'),
    path('reklama/<int:pk>/', ReklamaDetail.as_view(), name='reklama-detail'),

    path('promo/', PromoCodeList.as_view(), name='promo-list'),
    path('promo/create/', PromoCodeCreate.as_view(), name='promo-create'),
    path('promo/<int:pk>/', PromoCodeDetail.as_view(), name='promo-detail'),

    path('favorites/', FavoriteAPIView.as_view(), name='favorite-detail'),
    path('favorites/add/', FavoriteBookCreateAPIView.as_view(), name='favorite-add'),
    path('favorites/<int:pk>/', FavoriteBookDeleteAPIView.as_view(), name='favorite-book-detail'),

    path('cart/', CartAPIView.as_view(), name='cart-detail'),
    path('cart/add/', CartItemCreateAPIView.as_view(), name='cart-item-add'),
    path('cart/apply_promo/', ApplyPromoCodeView.as_view(), name='apply-promo'),
    path('cart/<int:pk>/', CartItemDetailAPIView.as_view(), name='cart-item-detail'),


    path('orders/', UserOrderListAPIView.as_view(), name='order-list'),
    path('orders/create/', CreateOrderAPIView.as_view(), name='order-create'),
    path('orders/seller/', SellerOrderListView.as_view(), name='seller-order-list'),
    path('orders/seller/<int:pk>/', SellerOrderUpdateView.as_view(), name='seller-order-update'),

    path('reviews/', ReviewListAPIView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', ReviewDetailAPIView.as_view(), name='review-detail'),

    path('comments/', CommentListAPIView.as_view(), name='comment-list'),


    path('orders/<int:order_id>/pay/', CreatePaymentView.as_view(), name='create-payment'),
    path('orders/<int:order_id>/payment-status/', PaymentStatusView.as_view(), name='payment-status'),
    path('payment/webhook/', finik_webhook, name='finik-webhook'),

]
