from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from recipes.models import (Ingredient, Tag, Recipe,
                            FavoriteRecipe, ShoppingCart)
from users.models import Subscribe, User
from django.db.models import Sum
from api.filters import IngredientFilter, RecipeFilter
from api.permissions import ReadOnly
from api.serializers import (CustomUserSerializer,
                             CustomUserWriteSerializer, UserPasswordSerializer,
                             IngredientSerializer, TokenSerializer,
                             TagSerializer, RecipeWriteSerializer,
                             RecipeSerializer, SubscribeSerializer,
                             ShoppingCartSerializer, FavoriteRecipeSerializer)

FILENAME = 'my_shopping_cart.txt'


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated, ReadOnly]

    def get_queryset(self):
        review = Subscribe.objects.filter(user=self.request.user)
        return review

    def get_serializer_context(self):
        context = super(SubscribeViewSet, self).get_serializer_context()
        followers = Subscribe.objects.all()
        context.update({'follow': followers})
        return context


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilter
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeWriteSerializer
        elif self.action == 'favorite':
            return FavoriteRecipeSerializer
        elif self.action == 'shopping_cart':
            return ShoppingCartSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super(RecipeViewSet, self).get_serializer_context()
        followers = Subscribe.objects.all()
        favorite = FavoriteRecipe.objects.all()
        shopping_cart = ShoppingCart.objects.all()
        context.update(
            {
                'follow': followers,
                'favorite': favorite,
                'shopping_cart': shopping_cart
            }
        )
        return context

    @action(
        detail=True,
        url_path='favorite',
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                recipe = get_object_or_404(Recipe, pk=pk)
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            favorite = FavoriteRecipe.objects.filter(
                recipe=pk, user=request.user
            )
            if favorite:
                favorite.delete()
                return Response(
                    {'message': f'Рецепт {pk} удален из избранного!'},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {'errors': 'Рецепт не добавлен в избранное!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True,
        url_path='shopping_cart',
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                recipe = get_object_or_404(Recipe, pk=pk)
                serializer.save(user=self.request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            shopping_cart = ShoppingCart.objects.filter(
                recipe=pk, user=request.user
            )
            if shopping_cart:
                shopping_cart.delete()
                return Response(
                    {'message': f'Рецепт {pk} удален из списка покупок!'},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {'errors': 'Рецепт не добавлен в список покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = self.request.user
        shopping_cart = (
            ShoppingCart.objects.filter(user=user).
            values(
                'recipe__ingredients__name',
                'recipe__ingredients__measurement_unit'
            ).annotate(amount=Sum('recipe__recipe__amount')).order_by())
        if shopping_cart:
            shopping_list = (
                'Список покупок: \n\n'
            )
            shopping_list += '\n'.join([
                f'{index}. {recipe["recipe__ingredients__name"]} '
                f'{recipe["amount"]} '
                f'({recipe["recipe__ingredients__measurement_unit"]})'
                for index, recipe in enumerate(shopping_cart, start=1)
            ])
        else:
            shopping_list = ('Cписок покупок отсутствует!')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={FILENAME}'
        return response


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    permission_classes = [ReadOnly]
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [ReadOnly]


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = LimitOffsetPagination
    serializer_class = CustomUserSerializer

    def get_serializer_context(self):
        context = super(UserViewSet, self).get_serializer_context()
        followers = Subscribe.objects.all()
        context.update({'follow': followers})
        return context

    def get_serializer_class(self):
        if self.action == 'subscribe':
            return SubscribeSerializer
        if self.request.method.lower() == 'post':
            return CustomUserWriteSerializer
        return CustomUserSerializer

    def perform_create(self, serializer):
        serializer.save(password=self.request.data['password'])

    @action(
        detail=True,
        url_path='subscribe',
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            data = {
                'user': request.user.id,
                'author': id
            }
            serializer = self.get_serializer(
                data=data,
                context={'request': request}
            )
            if serializer.is_valid():
                user = serializer.validated_data['user']
                author = get_object_or_404(User, pk=id)
                if user.id == int(id):
                    return Response(
                        {'errors': 'На самого себя не подписаться!'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if user.follower.filter(user=author).exists():
                    return Response(
                        {'errors': 'Вы уже подписались!'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user = request.user
            author = get_object_or_404(User, pk=id)
            follow = Subscribe.objects.filter(user=user, author=author)
            if follow:
                follow.delete()
                return Response(
                    {'message': 'Вы отписались!'},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {'errors': 'Подписки нет!'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AuthToken(ObtainAuthToken):
    serializer_class = TokenSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
            status=status.HTTP_201_CREATED
        )


@api_view(['post'])
def set_password(request):
    serializer = UserPasswordSerializer(data=request.data,
                                        context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Пароль перезаписан!'},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
