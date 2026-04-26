from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, viewsets, generics, permissions, response
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django_rest_passwordreset.models import ResetPasswordToken

User = get_user_model()


class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_code = serializers.IntegerField()
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        reset_code = data.get('reset_code')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("Пароли не совпадают.")

        try:
            token = ResetPasswordToken.objects.get(user__email=email, key=str(reset_code))
        except ResetPasswordToken.DoesNotExist:
            raise serializers.ValidationError("Неверный код сброса или email.")

        data['user'] = token.user
        data['token'] = token
        return data

    def save(self):
        user = self.validated_data['user']
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        # Удаляем использованный токен
        token.delete()


class ChangePasswordSerializer(serializers.Serializer):
    model = UserProfile
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


# ✅ ДОБАВИЛИ — сериализатор профиля
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'phone_number', 'user_role', 'profile_image'
        )
        # email и роль менять нельзя
        read_only_fields = ('email', 'user_role')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','email','phone_number','password','first_name','last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'phone_number': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует")
        return value

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Номер телефона обязателен")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Пользователь с таким номером уже существует")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)

        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'phone_number': str(instance.phone_number),
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class CustomLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Пользователь с таким email не найден"})

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Неверный пароль"})

        if not user.is_active:
            raise serializers.ValidationError("Пользователь не активен")

        self.context['user'] = user
        return data

    def to_representation(self, instance):
        user = self.context['user']
        refresh = RefreshToken.for_user(user)

        return {
            'user': {
                'username': user.username,
                'email': user.email,
                'user_role': user.user_role,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get('refresh')
        try:
            RefreshToken(token)
        except Exception:
            raise serializers.ValidationError({"refresh": "Невалидный токен"})
        return attrs


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields =('id', 'username', 'email', 'first_name', 'last_name','phone_number','user_role')


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields =('id', 'username', 'email', 'first_name', 'last_name','phone_number','user_role')


class StoreCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'
        read_only_fields = ['store_owner']





class StoreListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id','store_image',)


class StoreDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id','store_name','store_image','is_active','store_description','social_network','contact_number')


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategoryListSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'category_name','books_count']

    def get_books_count(self, obj):
        return obj.books_set.count()


class CategorySimpleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name',]



class CategoryDetailSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()


    class Meta:
        model = Category
        fields = ['id','category_name','books_count','position']

    def get_books_count(self, obj):
        return obj.books_set.count()



class BookImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImages
        fields = ['id','book','books_image']


class SaleListSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()
    is_currently_active = serializers.SerializerMethodField()
    class Meta:
        model = Sale
        fields = ['id', 'discount_percent', 'discounted_price', 'is_currently_active']


    def get_discounted_price(self, obj):
        return obj.discounted_price


    def get_is_currently_active(self, obj):
        return obj.is_currently_active


class SaleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ['is_active', 'discount_percent', 'start_date', 'end_date']


class BookCreateSerializer(serializers.ModelSerializer):
    store = serializers.PrimaryKeyRelatedField(read_only=True)
    images = BookImgSerializer(many=True, read_only=True)
    class Meta:
        model = Books
        fields = '__all__'


class BooksListSerializer(serializers.ModelSerializer):
    images = BookImgSerializer(many=True, read_only=True)
    sales = SaleListSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    count_rating = serializers.SerializerMethodField()
    good_rate = serializers.SerializerMethodField()
    class Meta:
        model = Books
        fields = ['id', 'books_name', 'author', 'price', 'sales', 'avg_rating', 'images','count_rating','good_rate','bestseller','position','new']


    def get_avg_rating(self, obj):
        return obj.avg_rating

    def get_count_rating(self, obj):
        return obj.get_count_rating()

    def get_good_rate(self, obj):
        return obj.good_rate




class SaleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'


class UserProfileReviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id','username')


class BooksMiniSerializers(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ('id', 'books_name')


class ReviewReplySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    parent_user_name = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = (
            'id',
            'user_name',
            'comment',
            'rating',
            'likes_count',
            'parent_user_name',
        )


    def get_parent_user_name(self, obj):
        if obj.parent:
            return obj.parent.user.username  # вот так берём имя родителя
        return None


class ReviewSerializers(serializers.ModelSerializer):
    user_reviews = UserProfileReviewSerializers(source='user', read_only=True)
    likes_count = serializers.ReadOnlyField()
    replies = serializers.SerializerMethodField()
    books  = BooksMiniSerializers(read_only=True)
    books_id = serializers.PrimaryKeyRelatedField(
        queryset=Books.objects.all(),
        source='books',
        write_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'user_reviews', 'books', 'rating', 'comment',
                  'created_at', 'likes_count', 'replies', 'parent', 'books_id',)


    def get_replies(self, obj):
        qs = obj.replies.all()
        return ReviewReplySerializer(qs, many=True).data


class ReviewDetailSerializers(serializers.ModelSerializer):
    user_reviews = UserProfileReviewSerializers(source='user', read_only=True)  # ✅
    likes_count = serializers.ReadOnlyField()
    replies = serializers.SerializerMethodField()  # вложенные ответы

    class Meta:
        model = Review
        fields = ('id', 'user_reviews', 'books', 'rating', 'comment',
                  'likes_count', 'created_at', 'replies', 'parent')
        read_only_fields = ['user', 'likes_count', 'created_at']

    def get_replies(self, obj):
        qs = obj.replies.all()
        return ReviewReplySerializer(qs, many=True).data



class BooksDetailSerializer(serializers.ModelSerializer):
    category = CategorySimpleListSerializer(read_only=True)
    sales = SaleListSerializer(many=True, read_only=True)
    review_books = ReviewSerializers(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    count_rating = serializers.SerializerMethodField()
    good_rate = serializers.SerializerMethodField()
    actual_price = serializers.SerializerMethodField()
    images = BookImgSerializer(many=True, read_only=True)

    class Meta:
        model = Books
        fields = ['books_name', 'price', 'bestseller', 'v_nalich', 'author', 'izdatelstvo', 'god_izdaniya',
                 'kolichestvo_stranits', 'format_knigi', 'age_limit', 'pereplet', 'isbn', 'yazyk',
                 'avg_rating', 'count_rating', 'good_rate', 'actual_price', 'category',
                  'sales', 'review_books','images','description','position','new']


    def get_avg_rating(self, obj):
        return obj.avg_rating


    def get_count_rating(self, obj):
        return obj.get_count_rating()


    def get_good_rate(self, obj):
        return obj.good_rate


    def get_actual_price(self, obj):
        return obj.get_actual_price()



class ReklamaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reklama
        fields = '__all__'


class ReklamaListSerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField(source='books_reklama.id', read_only=True)
    book_name = serializers.CharField(source='books_reklama.books_name', read_only=True)
    books_category = CategorySimpleListSerializer(read_only=True)
    class Meta:
        model = Reklama
        fields = ['id', 'title', 'description', 'image', 'link','books_reklama','book_id','book_name','books_category']


class ReklamaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reklama
        fields = ['title', 'description', 'image', 'link', 'status', 'created_at','books_reklama','position']


class PromoCodeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields  = '__all__'
        read_only_fields = ['seller', 'is_used', 'used_by',]


class PromoCodeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ['id', 'code', 'discount_percent', 'is_used',]


class PromoCodeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'


class PromoCodeApplySerializer(serializers.Serializer):
    code = serializers.CharField() # код потверждения


class FavoriteBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteBook
        fields = '__all__'
        read_only_fields = ['favorite']


class FavoriteSerializer(serializers.ModelSerializer):
    fav_product = FavoriteBookSerializer(many=True, read_only=True)
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'fav_product']


class CartItemBookSerializer(serializers.ModelSerializer):
    images = BookImgSerializer(many=True, read_only=True)

    class Meta:
        model = Books
        fields = ['id', 'books_name', 'author', 'price', 'images']

class CartItemSerializer(serializers.ModelSerializer):
    # ✅ ДОБАВИЛИ — чтобы фронт видел сумму по позиции
    total_price = serializers.ReadOnlyField()
    # total_price_with_promo = serializers.ReadOnlyField()
    books = CartItemBookSerializer(read_only=True)          # ✅ вложенные данные книги
    books_id = serializers.PrimaryKeyRelatedField(          # ✅ для записи (POST/PUT)
        queryset=Books.objects.all(),
        source='books',
        write_only=True
    )


    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ['cart']


class CartSerializer(serializers.ModelSerializer):
    # ✅ ДОБАВИЛИ — чтобы фронт видел итоговые суммы
    total_price = serializers.ReadOnlyField()
    total_price_with_promo = serializers.ReadOnlyField()
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = '__all__'




class OrderItemSerializer(serializers.ModelSerializer):
    books_name = serializers.CharField(source='books.books_name',read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            'id','books','books_name','price','quantity','total_price',)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    promo_code = PromoCodeListSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'status','total_price','created_at','items','phone_number','address','promo_code','region')

    def get_discount_percent(self, obj):
        if obj.promo_code:
            return obj.promo_code.discount_percent
        return 0


class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = '__all__'

class CommentLikeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = '__all__'
