from django.utils import timezone
from django.db.models import Avg
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from multiselectfield import MultiSelectField

from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # Укажи свой реальный домен
    frontend_url = "https://example.com"  # Заменить на адрес твоего сайта или фронтенда

    # Генерация полного URL сброса пароля
    reset_url = "{}{}?token={}".format(
        frontend_url,
        reverse('password_reset:reset-password-request'),  # Django-обработчик, можно заменить
        reset_password_token.key
    )

    # Отправка письма
    send_mail(
        subject="Password Reset for Some Website",  # Тема
        message=f"Use the following link to reset your password:\n{reset_url}",  # Текст
        from_email="noreply@example.com",  # Отправитель
        recipient_list=[reset_password_token.user.email],  # Получатель
        fail_silently=False,
    )


class UserProfile(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    ROLE_CHOICES = (
        ('seller', 'seller'),
        ('client', 'client')
    )
    user_role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    profile_image = models.ImageField(upload_to='profile_image/', null=True, blank=True)

    def __str__(self):
        return f'{self.username}, {self.user_role}'

class Store(models.Model):
    store_owner = models.OneToOneField(UserProfile,on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100)
    store_region = models.CharField(max_length=100)
    store_image = models.ImageField(upload_to='store_image',null=True,blank=True)
    store_description = models.TextField(max_length=500,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    contact_number = PhoneNumberField(region='KG',null=True,blank=True)
    social_network = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.store_name

class Category(models.Model):
    category_name = models.CharField(max_length=500)
    category_icon =  models.ImageField(upload_to='category_icon/', null=True, blank=True)

    def __str__(self):
        return self.category_name


class Books(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE,null=True,blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    books_name = models.CharField(max_length=500, null=True, blank=True, verbose_name="Название книги")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена")
    description = models.TextField(null=True,blank=True)
    bestseller = models.BooleanField(default=False, verbose_name="Бестселлер")

    VNALICHI_CHOICES = (
        ('БИШКЕК', 'БИШКЕК'),
        ('ОШ', 'ОШ'),
        ('Бишкек,Oш', 'Бишкек,Oш'),

    )
    v_nalich = models.CharField(max_length=26,choices= VNALICHI_CHOICES,null=True, blank=True, verbose_name="Наличие")
    author = models.CharField(max_length=500, null=True, blank=True, verbose_name="Автор")
    izdatelstvo = models.CharField(max_length=500, null=True, blank=True, verbose_name="Издательство")
    god_izdaniya = models.IntegerField(null=True, blank=True, verbose_name="Год издания")
    kolichestvo_stranits = models.IntegerField(null=True, blank=True, verbose_name="Количество страниц")
    format_knigi = models.CharField(max_length=100, null=True, blank=True, verbose_name="Формат")
    age_limit =  models.PositiveSmallIntegerField(validators=[ MinValueValidator(1),MaxValueValidator(90)],null=True, blank=True)


    PEREPLET_CHOICES = (
        ('Твердый переплет', 'Твердый переплет'),
        ('Мягкий переплет', 'Мягкий переплет'),
    )
    pereplet = models.CharField(max_length=16, choices=PEREPLET_CHOICES, null=True, blank=True, verbose_name="Переплет")
    isbn = models.CharField(max_length=64, null=True, blank=True, verbose_name="ISBN")
    tirazh = models.IntegerField(null=True, blank=True, verbose_name="Тираж")
    yazyk = models.CharField(max_length=64, null=True, blank=True, verbose_name="Язык")
    artikul = models.CharField(max_length=64, null=True, blank=True, verbose_name="Артикул", unique=True)


    @property
    def avg_rating(self):
        avg = self.review_books.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg else 0

    def get_count_rating(self):
        count = self.review_books.count()
        if count > 3:
            return '3+'
        return count

    @property
    def good_rate(self):
        total = self.review_books.count()
        if total == 0:
            return '0%'
        good = self.review_books.filter(rating__gt=3).count()
        percent = round((good * 100) / total)
        return f'{percent}%'


    def get_actual_price(self):
        sale = self.sales.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()

        if sale:
            return sale.discounted_price

        return self.price

    def __str__(self):
        return str(self.books_name)


class Sale(models.Model):
    books = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='sales')
    is_active = models.BooleanField(default=True)
    description1 = models.TextField(null=True,blank=True)
    description2 = models.TextField(null=True,blank=True)
    discount_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    @property
    def discounted_price(self):
        if self.discount_percent and self.books.price:
            return self.books.price * (Decimal(100) - self.discount_percent) / Decimal(100)

        return self.books.price

    @property
    def is_currently_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date



    def __str__(self):
        return f"{self.books.books_name} - {self.discount_percent}%"


class BookImages(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='images')
    books_image = models.ImageField(upload_to='book_image/', null=True, blank=True)

    def __str__(self):
        return str(self.books_image) or str(self.book)


class Reklama(models.Model):
    title = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='reklama_image/', null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    STATUS_CHOICES = (
        ('Активный', 'Активный'),
        ('Неактивный', 'Неактивный'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Активный')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PromoCode(models.Model):
    seller = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='promo_codes')
    code = models.CharField(max_length=50, unique=True,null=True,blank=True)  # сам промокод например "SALE20"
    discount_percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],null=True,blank=True
    )
    is_used = models.BooleanField(default=False)  # использован или нет
    used_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='used_promos'
    )  # кто использовал
    created_at = models.DateTimeField(auto_now_add=True)

    def apply(self, user, cart):
        # Проверяем не использован ли уже
        if self.is_used:
            return None, "Промокод уже использован"

        # Считаем скидку
        discount = cart.total_price * Decimal(self.discount_percent) / Decimal(100)
        new_price = cart.total_price - discount

        # Помечаем как использованный
        self.is_used = True
        self.used_by = user
        self.save()

        return new_price, "Промокод применён успешно"

    def __str__(self):
        return f"{self.code} - {self.discount_percent}% ({'использован' if self.is_used else 'активен'})"


class Favorite(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='favorite')

    def __str__(self):
        return f'{self.user}'


class FavoriteBook(models.Model):
    books = models.ForeignKey(Books, on_delete=models.CASCADE)
    favorite = models.ForeignKey(Favorite, on_delete=models.CASCADE, related_name='fav_product')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('favorite', 'books')

    def __str__(self):
        return f'{self.books} - {self.favorite}'


class Cart(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    promo_code = models.ForeignKey('PromoCode',on_delete=models.SET_NULL, null=True, blank=True  # корзина может быть без промокода
                                                                                            )

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all()) or Decimal('0.00')

    @property
    def total_price_with_promo(self):
        total = self.total_price

        # Если промокод есть
        if self.promo_code:
            discount = total * Decimal(self.promo_code.discount_percent) / Decimal(100)
            return total - discount

        # Если промокода нет - обычная цена
        return total

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    books = models.ForeignKey(Books, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        price = self.books.get_actual_price()
        if price is None:
            return Decimal('0.00')
        return price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.books.books_name}"


class Order(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_orders')
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)
    STATUS_CHOICES = (
        ('Ожидании', 'Ожидании'),
        ('Отправлен', 'Отправлен'),
        ('Доставлен', 'Доставлен'),
        ('Отменён', 'Отменён'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ожидании')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f'Order #{self.id} - {self.user.username}'

    def calculate_total(self):
        total = sum(item.total_price for item in self.items.all())

        # Если есть промокод — применяем скидку
        if self.promo_code:
            discount = total * Decimal(self.promo_code.discount_percent) / Decimal(100)
            total = total - discount

        self.total_price = total
        self.save(update_fields=['total_price'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    books = models.ForeignKey(Books, on_delete=models.PROTECT, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # Автоматически берём актуальную цену при создании
        if self.price is None:
            self.price = self.books.get_actual_price() or Decimal('0.00')
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.books.books_name}"


class Review(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_reviews')
    books = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='review_books')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)



    def is_reply(self):
        return self.parent is not None

    @property
    def likes_count(self):
        return self.likes.count()

    def __str__(self):
        if self.is_reply():
            return f"Reply by {self.user.username} to Review {self.parent.id}"
        return f"Review by {self.user.username} on {self.books.books_name}"


class CommentLike(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        return f'{self.user} - {self.review}'




class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    finik_payment_id = models.CharField(max_length=255, unique=True)
    qr_url = models.URLField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'PENDING'),
            ('PAID', 'PAID'),
            ('REJECTED', 'REJECTED')
        ],
        default='PENDING'
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Payment for Order #{self.order.id} - {self.status}'