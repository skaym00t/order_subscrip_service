from django.contrib import admin

from .models import CustomUser, Executor



@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Админка для модели CustomUser"""
    list_display = ('username', 'email', 'phone', 'chat_id', 'first_name', 'last_name', 'is_staff', 'is_executor', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email', 'phone', 'chat_id', 'is_executor')}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'username', 'email', 'phone', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'is_staff'),
        }),
    )

@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    """Админка для модели Executor"""
    list_display = ('id', 'user', 'specialty', 'rating')
    search_fields = ('user__username', 'specialty')
    list_filter = ('rating',)

    class Meta:
        model = Executor