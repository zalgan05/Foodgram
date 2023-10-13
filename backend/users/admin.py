from django.contrib import admin
from .models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'recipes_count', 'following_count')
    list_filter = ('username', 'email')

    @admin.display(description='Кол-во рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Кол-во подписчиков')
    def following_count(self, obj):
        return obj.following.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    list_filter = ('user',)
