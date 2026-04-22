import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash

from rest_framework import viewsets, generics, permissions, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.exceptions import ValidationError as DjangoValidationError
from .filters import BookFilter
from .models import *
from .serializers import *
from .services import *
from .finik import *



# ─── Reset password ────────────────────────────────────────────────────────────

@api_view(['POST'])
def verify_reset_code(request):
    serializer = VerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Пароль успешно сброшен.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if user.check_password(serializer.data.get('old_password')):
            user.set_password(serializer.data.get('new_password'))
            user.save()
            update_session_auth_hash(request, user)
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── User ──────────────────────────────────────────────────────────────────────

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomLoginView(generics.GenericAPIView):
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'detail': 'Невалидный токен'}, status=status.HTTP_400_BAD_REQUEST)


class SellerAPIView(generics.ListAPIView):
    serializer_class = SellerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)


class ClientAPIView(generics.ListAPIView):
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)


# ─── Store ─────────────────────────────────────────────────────────────────────

class StoreListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StoreCreateSerializers
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Store.objects.filter(store_owner=self.request.user)

    def perform_create(self, serializer):
        if Store.objects.filter(store_owner=self.request.user).exists():
            raise serializers.ValidationError("У вас уже есть магазин")
        serializer.save(store_owner=self.request.user)


class StoreListAPIView(generics.ListAPIView):
    serializer_class = StoreListSerializers
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Store.objects.filter(store_owner=self.request.user)


class StoreDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StoreDetailSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Store.objects.none()
        return Store.objects.filter(store_owner=self.request.user)


# ─── Category ──────────────────────────────────────────────────────────────────

class CategoryCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


# ─── Books ─────────────────────────────────────────────────────────────────────

class BooksCreateAPIView(generics.CreateAPIView):
    queryset = Books.objects.all()
    serializer_class = BookCreateSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        try:
            store = Store.objects.get(store_owner=self.request.user)
        except Store.DoesNotExist:
            raise serializers.ValidationError("У вас нет магазина. Сначала создайте магазин.")
        serializer.save(store=store)


class BooksListAPIView(generics.ListAPIView):
    queryset = Books.objects.all()
    serializer_class = BooksListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['books_name', 'author', 'izdatelstvo']
    ordering_fields = ['price', 'god_izdaniya']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['total_books'] = Books.objects.count()
        return response

class BooksDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Books.objects.all()
    serializer_class = BooksDetailSerializer


class BookImageListAPIView(generics.ListCreateAPIView):
    queryset = BookImages.objects.all()
    serializer_class = BookImgSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


class BookImageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BookImages.objects.all()
    serializer_class = BookImgSerializer


class BookPositionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            book = Books.objects.get(pk=pk)
        except Books.DoesNotExist:
            return Response({'error': 'Книга не найдена'}, status=404)

        new_position = request.data.get('position')
        if new_position is None:
            return Response({'error': 'Укажите position'}, status=400)

        old_position = book.position

        # Временно ставим 9999 чтобы не было одинаковых позиций
        Books.objects.filter(pk=pk).update(position=9999)

        # Книге на новой позиции даём старую позицию
        Books.objects.filter(position=new_position).exclude(pk=pk).update(position=old_position)

        # Теперь ставим нашей книге новую позицию
        Books.objects.filter(pk=pk).update(position=new_position)

        return Response({'message': f'Позиция изменена: {old_position} ↔ {new_position}'})

# ─── Sale ──────────────────────────────────────────────────────────────────────

class SaleCreateAPIView(generics.ListCreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class SaleList(generics.ListAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleListSerializer


class SaleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


# ─── Reklama ───────────────────────────────────────────────────────────────────

class ReklamaCreate(generics.CreateAPIView):
    queryset = Reklama.objects.all()
    serializer_class = ReklamaCreateSerializer


class ReklamaList(generics.ListAPIView):
    queryset = Reklama.objects.all()
    serializer_class = ReklamaListSerializer


class ReklamaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reklama.objects.all()
    serializer_class = ReklamaDetailSerializer


# ─── PromoCode ─────────────────────────────────────────────────────────────────

class PromoCodeCreate(generics.CreateAPIView):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class PromoCodeList(generics.ListAPIView):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeListSerializer


class PromoCodeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeDetailSerializer


class ApplyPromoCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Введите промокод'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            promo = PromoCode.objects.get(code=code, is_used=False)
        except PromoCode.DoesNotExist:
            return Response({'error': 'Промокод не найден или уже использован'}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.promo_code = promo
        cart.save()

        return Response({
            'message': f'Промокод применён. Скидка {promo.discount_percent}%',
            'total_price': str(cart.total_price),
            'total_price_with_promo': str(cart.total_price_with_promo),
        })


# ─── Favorite ──────────────────────────────────────────────────────────────────

class FavoriteAPIView(generics.RetrieveAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        favorite, _ = Favorite.objects.get_or_create(user=self.request.user)
        return favorite


class FavoriteBookCreateAPIView(generics.CreateAPIView):
    queryset = FavoriteBook.objects.all()
    serializer_class = FavoriteBookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        favorite, _ = Favorite.objects.get_or_create(user=self.request.user)
        books = serializer.validated_data['books']
        if FavoriteBook.objects.filter(favorite=favorite, books=books).exists():
            raise serializers.ValidationError("Эта книга уже в избранном")
        serializer.save(favorite=favorite)


class FavoriteBookDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FavoriteBookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return FavoriteBook.objects.none()
        return FavoriteBook.objects.filter(favorite__user=self.request.user)


# ─── Cart ──────────────────────────────────────────────────────────────────────

class CartAPIView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemCreateAPIView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        books = serializer.validated_data['books']
        quantity = serializer.validated_data.get('quantity', 1)
        existing = CartItem.objects.filter(cart=cart, books=books)
        if existing.exists():
            cart_item = existing.first()
            existing.exclude(pk=cart_item.pk).delete()
            cart_item.quantity += quantity
            cart_item.save()
        else:
            serializer.save(cart=cart)


class CartItemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CartItem.objects.none()
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_update(self, serializer):
        quantity = serializer.validated_data.get('quantity')
        if quantity <= 0:
            serializer.instance.delete()
        else:
            serializer.save()


# ─── Order ─────────────────────────────────────────────────────────────────────

class UserOrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        address = request.data.get('address')
        region = request.data.get('region')


        if not phone_number or not address or not region:
            return Response(
                {'error': 'Укажите телефон,регион и адрес доставки'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            order = create_order_from_cart(request.user, phone_number, address,region)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except DjangoValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)


class SellerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(
            items__books__store__store_owner=self.request.user
        ).distinct()

class UserOrderDeleteAPIView(generics.DestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)


class SellerOrderUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(
            items__books__store__store_owner=self.request.user
        ).distinct()

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get('status')
        allowed = ['Ожидании', 'Отправлен', 'Оплачен', 'Отменён']
        if new_status not in allowed:
            return Response({'error': 'Неверный статус'}, status=400)
        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)


# ─── Review ────────────────────────────────────────────────────────────────────

class ReviewListAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializers
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializers
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentListAPIView(generics.ListCreateAPIView):
    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer




class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=404)

        # Проверяем — уже оплачен?
        pre = FinikPrePayment.objects.filter(order=order).first()
        if pre and pre.status == FinikPrePayment.Status.SUCCESS:
            return Response({'error': 'Заказ уже оплачен'}, status=400)

        try:
            finik = FinikClient()
            payment_data = finik.create_payment(
                user=request.user,
                amount=int(order.total_price),
                order=order,
            )
        except Exception as e:
            return Response({'error': str(e)}, status=502)

        pre_payment, _ = FinikPrePayment.objects.update_or_create(
            order=order,
            defaults={
                'user': request.user,
                'amount': order.total_price,
                'provider_order_id': payment_data.get('payment_id'),
                'provider_response': payment_data,
                'payment_url': payment_data.get('payment_url'),
                'status': FinikPrePayment.Status.REDIRECTED,
            }
        )

        return Response({'payment_url': payment_data.get('payment_url')}, status=201)


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            pre = order.pre_payment
        except (Order.DoesNotExist, FinikPrePayment.DoesNotExist):
            return Response({'error': 'Платёж не найден'}, status=404)

        return Response({
            'status': pre.status,
            'payment_url': pre.payment_url,
            'amount': str(pre.amount),
        })


@csrf_exempt
def finik_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse('Bad JSON', status=400)

    fields = data.get("fields", {})
    payment_id = fields.get("paymentId") or data.get("transactionId")
    finik_status = (data.get("status") or "").lower()

    # Дедупликация
    if FinikPostPayment.objects.filter(payment_id=payment_id, status="SUCCESS").exists():
        return HttpResponse('Already processed', status=200)

    # Маппинг статусов
    status_map = {
        "succeeded": "SUCCESS",
        "failed": "FAILED",
        "cancelled": "CANCELLED",
        "created": "PENDING",
    }
    mapped_status = status_map.get(finik_status, "PENDING")

    post_payment = FinikPostPayment.objects.create(
        payment_id=payment_id,
        status=mapped_status,
        amount=data.get("amount", 0),
        raw_data=data,
    )

    pre_payment = FinikPrePayment.objects.filter(provider_order_id=payment_id).first()

    if pre_payment:
        post_payment.paying_user = pre_payment.user
        post_payment.save(update_fields=["paying_user"])

        pre_payment.status = mapped_status
        pre_payment.save(update_fields=["status"])

        if mapped_status == "SUCCESS":
            handle_payment_success(pre_payment)

    return HttpResponse('OK', status=200)