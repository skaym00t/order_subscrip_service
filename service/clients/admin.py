from django.contrib import admin

from .models import CustomUser, Executor


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # Поля, отображаемые в списке пользователей
    list_display = ('username', 'email', 'phone', 'first_name', 'last_name', 'is_staff', 'is_active')
    # Поля, по которым можно фильтровать
    list_filter = ('is_staff', 'is_active', 'groups')
    # Поля, по которым можно искать
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    # Порядок сортировки
    ordering = ('username',)

    # Поля для формы редактирования/создания
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    # Поля для формы добавления нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'username', 'email', 'phone', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'is_staff'),
        }),
    )

@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'specialty', 'rating')
    search_fields = ('user__username', 'specialty')
    list_filter = ('rating',)

    class Meta:
        model = Executor