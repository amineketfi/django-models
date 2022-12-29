from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal


# Custom Query Set
class ProductInStockQuerySet(models.QuerySet):
    def in_stock(self):
        return self.filter(stock__count__gt=0)

class Product(models.Model):
    name = models.CharField(max_length=100)
    stock_count = models.IntegerField(help_text="How many items are currently in stock")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(default='')
    sku = models.CharField(unique=True, max_length=20, verbose_name="Stock Keeping Unit", default='')
    slug = models.SlugField()

    # Adding a custom manager require adding the default one
    objects = models.Manager()
    in_stock = ProductInStockQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    # The Meta class is used to add configs to the Model class
    class Meta:
        ordering = ['price']
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0),
                                    name="price_not_negative")
        ]

    def get_absolute_url(self):
        return reverse("store:product-detail", kwargs={'pk': self.id})

    @property # convert the method to property
    def vat(self):
        return Decimal(.2) * self.price

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    image = models.ImageField()
    Product = models.ForeignKey('Product', on_delete=models.CASCADE)

    def __str__(self):
        return self.image

class Category(models.Model):
    name = models.CharField(max_length=150)
    products = models.ManyToManyField('Product') 
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name