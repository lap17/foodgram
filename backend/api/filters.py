import django_filters as filters

from users.models import User
from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_in_shopping_cart = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(),
        method='get_is_in_shopping_cart',
        label='В корзине'
    )
    is_favorited = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(),
        method='get_is_favorited',
        label='В избранных'
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Ссылка'
    )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    def get_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ["is_favorited", "is_in_shopping_cart", "author", "tags"]
