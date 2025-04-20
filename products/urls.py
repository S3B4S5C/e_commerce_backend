from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='api-product-list'),
    path('registerProduct', views.register_product, name='api-product-register'),
    path('search', views.search_products, name='search-products'),
    path('searchProducts', views.search_product, name='search-products'),
    path('categories', views.get_product_categories, name='get-product-categories'),
    path('tags/create', views.create_tag, name='create-tag'),
    path('tags/delete/<uuid:tag_id>', views.delete_tag, name='delete-tag'),
    path('tags/associate', views.associate_tag_to_product, name='associate-tag-product'),
    path('tags/remove', views.remove_tag_from_product, name='remove-tag-product'),
    path('tags/product/<uuid:product_id>', views.get_tags_for_product, name='get-tags-product'),
    path('reviews/create/<uuid:product_id>', views.create_review, name='create-review'),
    path('reviews/delete/<uuid:review_id>', views.delete_review, name='delete-review'),
    path('favorites/add/<uuid:product_id>', views.add_to_favorites, name='add-favorites'),
    path('favorites/remove/<uuid:product_id>', views.remove_from_favorites, name='remove-favorites'),
    path('products/update/<uuid:product_id>', views.update_product, name='update-product'),
    path('products/delete/<uuid:product_id>', views.delete_product, name='delete-product'),
    path('favorites', views.get_favorite_products, name='get-favorite-products'),
    path('favoritesmost', views.get_most_favorited_products, name='get-most_favorited-products'),
    path('randomproducts', views.get_random_product, name='get-random-products'),
    path('recommended', views.get_recommendations, name='get-recommendations'),
]
