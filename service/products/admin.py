from django.contrib import admin

from products.models import Executor, Order


@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'specialty', 'rating')
    search_fields = ('user__username', 'specialty')
    list_filter = ('rating',)

    class Meta:
        model = Executor


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
