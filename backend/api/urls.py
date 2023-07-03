from django.urls import include, path, re_path
from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from api.views import (
    SubscribeViewSet,
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
    CustomUserViewSet,
    AuthToken,
    set_password
)

app_name = 'api'

router = DefaultRouter()
router.register(
    'users/subscriptions', SubscribeViewSet, basename='subscriptions'
    )
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet, basename='tags')
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('users/set_password/', set_password, name='set_password'),
    path('auth/token/login/', AuthToken.as_view(), name='login'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/token/logout/?$', TokenDestroyView.as_view(),
            name='logout'),
    path('auth/', include('djoser.urls.authtoken')),
]
