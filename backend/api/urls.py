from django.urls import include, path
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.routers import DefaultRouter

from .views import (
    FollowListView,
    FollowView,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet
)

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', DjoserUserViewSet)

urlpatterns = [
    path('users/subscriptions/', FollowListView.as_view()),
    path('users/<int:pk>/subscribe/', FollowView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
