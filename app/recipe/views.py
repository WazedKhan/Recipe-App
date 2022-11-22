"""
Views for the recipe app
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipe for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)


class BaseRecipeAttrViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin,
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Base view set for recipe attributes"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter querset to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')  # type: ignore # noqa


class TagViewSet(BaseRecipeAttrViewSet):
    """Views for tag API"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredient in the database(Ingredient View)"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
