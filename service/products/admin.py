from django.contrib import admin

from products.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'executor',
        'title',
        'status',
        'price',
        'created_at',
        'updated_at',
        'description'
    )

    class Meta:
        model = Order
