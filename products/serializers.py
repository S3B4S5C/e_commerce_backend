from rest_framework import serializers
from .models import Product, Tag, ProductReview, Stock
from django.db.models import Sum


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ProductReviewPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['id', 'rating', 'comment', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    previews = serializers.SerializerMethodField()
    favorite_count = serializers.IntegerField(read_only=True)
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_tags(self, obj):
        tags = Tag.objects.filter(tagged__product=obj)
        return TagSerializer(tags, many=True).data

    def get_previews(self, obj):
        reviews = ProductReview.objects.filter(product=obj).order_by('-created_at')[:3]  # últimas 3
        return ProductReviewPreviewSerializer(reviews, many=True).data

    def get_total_stock(self, obj):
        total = Stock.objects.filter(product=obj).aggregate(total=Sum('quantity'))['total']
        return total or 0
