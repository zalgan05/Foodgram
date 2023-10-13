from django.contrib import admin

from .models import Ingredient, IsFavoriteRecipe, Recipe, RecipeIngredient, Tag


class IngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'tags_list',
        'ingredients_list',
        'count__is_favorited'
    )
    list_filter = (
        'pub_date',
        'author__username',
        'tags__name',
        'ingredients__name'
    )
    inlines = [
        IngredientInline,
    ]
    fields = ('name', 'author', 'image', 'text', 'tags', 'cooking_time')

    @admin.display(description='Тэги')
    def tags_list(self, row):
        return ','.join([x.name for x in row.tags.all()])

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, row):
        return ','.join([x.name for x in row.ingredients.all()])

    @admin.display(description='Добавлений в избранное')
    def count__is_favorited(self, obj):
        return obj.is_favorite.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(IsFavoriteRecipe)
class IsFavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
    list_filter = ('recipe__name',)
