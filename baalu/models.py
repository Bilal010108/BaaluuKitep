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
    category_name = models.CharField(max_length=500,null=True,blank=True)
    position = models.PositiveIntegerField(default=0, verbose_name="Позиция",null=True,blank=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            last = Category.objects.aggregate(max_pos=models.Max('position'))['max_pos']
            self.position = (last or 0) + 1
        super().save(*args, **kwargs)




    def __str__(self):
        return self.category_name

    class Meta:
        ordering = ['position']

class Books(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE,null=True,blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    books_name = models.CharField(max_length=500, null=True, blank=True, verbose_name="Название книги")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(null=True,blank=True)
    bestseller = models.BooleanField(default=False, verbose_name="Бестселлер")

    VNALICHI_CHOICES = (
        ('БИШКЕК', 'БИШКЕК'),
        ('ОШ', 'ОШ'),
        ('Бишкек,Oш', 'Бишкек,Oш'),
        ('В наличи нет', 'В наличи нет'),

    )
    v_nalich = models.CharField(max_length=26,choices= VNALICHI_CHOICES,null=True, blank=True, verbose_name="Наличие")
    author = models.CharField(max_length=500, null=True, blank=True, verbose_name="Автор")
    izdatelstvo = models.CharField(max_length=500, null=True, blank=True, verbose_name="Издательство")
    god_izdaniya = models.IntegerField(null=True, blank=True, verbose_name="Год издания")
    kolichestvo_stranits = models.IntegerField(null=True, blank=True, verbose_name="Количество страниц")
    format_knigi = models.CharField(max_length=100, null=True, blank=True, verbose_name="Формат")
    age_limit =  models.PositiveSmallIntegerField(validators=[ MinValueValidator(0),MaxValueValidator(90)],null=True, blank=True)


    PEREPLET_CHOICES = (
        ('Твердый переплет', 'Твердый переплет'),
        ('Мягкий переплет', 'Мягкий переплет'),
    )
    pereplet = models.CharField(max_length=16, choices=PEREPLET_CHOICES, null=True, blank=True, verbose_name="Переплет")
    isbn = models.CharField(max_length=64, null=True, blank=True, verbose_name="ISBN")
    yazyk = models.CharField(max_length=64, null=True, blank=True, verbose_name="Язык")
    position = models.PositiveIntegerField(default=0, verbose_name="Позиция",null=True,blank=True)



    @property
    def avg_rating(self):
        avg = self.review_books.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg else 0

    def get_count_rating(self):
        count = self.review_books.count()
        if count > 500:
            return '500+'
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

    def save(self, *args, **kwargs):
        if self.pk is None:
            last = Books.objects.aggregate(max_pos=models.Max('position'))['max_pos']
            self.position = (last or 0) + 1
        super().save(*args, **kwargs)



    def __str__(self):
        return str(self.books_name)

    class Meta:
        ordering = ['position']



class Sale(models.Model):
    books = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='sales')
    is_active = models.BooleanField(default=True)
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
    books_reklama = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='reklama',null=True, blank=True)
    books_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='reklama_category',null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='reklama_image/', null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    STATUS_CHOICES = (
        ('Активный', 'Активный'),
        ('Неактивный', 'Неактивный'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Активный')
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(default=0, verbose_name="Позиция",null=True,blank=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            last = Reklama.objects.aggregate(max_pos=models.Max('position'))['max_pos']
            self.position = (last or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['position']


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
        ('Оплачен', 'Оплачен'),
        ('Отменён', 'Отменён'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ожидании')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    REGION_CHOICES = (
        ('ОШ', 'ОШ'),
        ('БИШКЕК', 'БИШКЕК'),
    )
    region = models.CharField(max_length=20, choices=REGION_CHOICES,blank=True,null=True)



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
    books = models.ForeignKey(Books, on_delete=models.CASCADE , related_name='order_items')
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


class FinikPrePayment(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Создан"
        REDIRECTED = "REDIRECTED", "Переход к оплате"
        SUCCESS = "SUCCESS", "Успешно"
        FAILED = "FAILED", "Ошибка"

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="finik_payments", verbose_name="Пользователь")
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='pre_payment', null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, verbose_name="Статус")
    provider_order_id = models.CharField(max_length=500, blank=True, null=True, verbose_name="ID заказа в Finik")
    provider_response = models.JSONField(default=dict, blank=True, verbose_name="Ответ от Finik")
    payment_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name="Ссылка на оплату")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Платёж перед оплатой"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"FinikPrePayment {self.id} — {self.amount} ({self.get_status_display()})"


class FinikPostPayment(models.Model):
    STATUS_CHOICES = [
        ("SUCCESS", "Успешный платёж"),
        ("FAILED", "Ошибка оплаты"),
        ("CANCELLED", "Отменён"),
        ("PENDING", "В обработке"),
    ]
    payment_id = models.CharField(max_length=500, verbose_name="ID платежа в Finik")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name="Статус")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    paying_user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="finik_post_payments")
    raw_data = models.JSONField(verbose_name="Сырой ответ от Finik")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Платёж после оплаты"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"FinikPostPayment {self.payment_id} — {self.status}"