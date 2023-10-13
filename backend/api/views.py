from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (Ingredient, IsFavoriteRecipe, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from .filters import IngredientFilter, RecipeFilter
from .pagination import FollowPagination
from .permissions import IsAdmin, IsAuthor, ReadOnly
from .serializers import (CreateSubscribeSerializer,
                          GetSubscriptionsSerializer, IngredientSerializer,
                          IsFavoriteSerializer,
                          RecipeCreateAndUpdateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Обрабатывает GET запросы для тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdmin | ReadOnly]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Обрабатывает GET запросы для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdmin | ReadOnly]
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Обрабатывает запросы GET для всех рецептов, POST - создаёт новый рецепт,
    GET, PATCH, DELETE для одного рецепта по id.
    """

    queryset = Recipe.objects.all()
    permission_classes = [ReadOnly | IsAdmin | IsAuthor]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateAndUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_ingredient_sum_in_shopping_cart(self):
        """Возвращает список сумм ингредиентов в корзине."""
        return RecipeIngredient.objects.filter(
            recipe__in_shopping_cart__user=self.request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Возвращает файл.txt со списком ингредиентов рецептов в корзине."""
        ingredients_sum = self.get_ingredient_sum_in_shopping_cart()
        current_ingredient = [(
            f'{ingredient["ingredient__name"]} '
            f'{ingredient["amount"]} '
            f'{ingredient["ingredient__measurement_unit"]}\n'
        ) for ingredient in ingredients_sum]
        file = ''.join(current_ingredient)
        content = (
            f'Ваш список покупок:\n'
            f'{file}'
        )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={}'.format('.txt')
        )
        return response

    @staticmethod
    def add_to(request, serializer_class, pk):
        """Создает связь рецепта с id=pk с текущим пользователем."""
        serializer = serializer_class(
            data=request.data,
            context={'request': request, 'recipe_id': pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_to(request, serializer_class, model, pk):
        """Удаляет связь рецепта с id=pk с текущим пользователем."""
        user = request.user
        serializer = serializer_class(
            data=request.data,
            context={'request': request, 'recipe_id': pk}
        )
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.filter(
            user=user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Обрабатывает запросы на добавление рецепта в избранное."""
        return self.add_to(
            request, IsFavoriteSerializer, pk
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        """Обрабатывает запросы на удаление рецепта из избранного."""
        return self.delete_to(
            request, IsFavoriteSerializer, IsFavoriteRecipe, pk
        )

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Обрабатывает запросы на добавление рецепта в корзину."""
        return self.add_to(
            request, ShoppingCartSerializer, pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        """Обрабатывает запросы на удаление рецепта из корзины."""
        return self.delete_to(
            request, ShoppingCartSerializer, ShoppingCart, pk
        )


class FollowListView(generics.ListAPIView):
    """Получение списка подписок на пользователей."""

    serializer_class = GetSubscriptionsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FollowPagination

    def get_queryset(self):
        return User.objects.filter(
            following__user=self.request.user
        )


class FollowView(APIView):
    """Обработка запросов на добавление/удаление подписки на пользователя."""

    permission_classes = [IsAuthenticated]
    pagination_class = FollowPagination

    def post(self, request, pk):
        follow_user = get_object_or_404(User, id=pk)
        data = {
            'user': request.user.id,
            'following': follow_user.id,
        }
        serializer = CreateSubscribeSerializer(
            data=data, context={'request': self.request, 'pk': pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        follow_user = get_object_or_404(User, id=pk)
        if not user.follower.filter(following=follow_user).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.follower.filter(following=follow_user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
