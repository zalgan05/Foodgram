from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet

from recipes.models import Ingredient, Recipe


class RecipeFilter(FilterSet):

    tags = CharFilter(field_name="tags__slug")
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(is_favorite__user=self.request.user)
            return queryset.exclude(is_favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(
                    in_shopping_cart__user=self.request.user
                )
            return queryset.exclude(in_shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
