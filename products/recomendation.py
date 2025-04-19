from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
from.models import Product, Tagged, Tag
from products.models import FavoriteProduct
from django.db.models import Count

def get_product_features_from_db():
    # Paso 1: Obtener todos los productos activos
    products = Product.objects.filter(deleted_at__isnull=True)

    # Paso 2: Construir un DataFrame base
    product_data = []
    for product in products:
        product_data.append({
            'id': str(product.id),
            'price': float(product.price),
            'category': product.category,
            'brand': product.brand,
        })

    df = pd.DataFrame(product_data)

    # Paso 3: Agregar tags como variables binarias (One-hot encoding de tags)
    tags = Tagged.objects.select_related('tag', 'product')
    for tag in tags:
        tag_name = tag.tag.name
        product_id = str(tag.product.id)
        if product_id in df['id'].values:
            df.loc[df['id'] == product_id, tag_name] = 1

    # Rellenar los NaNs en columnas de tags con 0 (ausencia del tag)
    df.fillna(0, inplace=True)

    # Paso 4: Codificar categoría y marca con one-hot encoding
    df = pd.get_dummies(df, columns=['category', 'brand'])

    # Paso 5: Devolver el DataFrame con ID por separado y solo las features numéricas
    product_ids = df['id']
    df.drop(columns=['id'], inplace=True)

    return df, product_ids

def recommend_products():
    # Paso 1: Obtener el DataFrame de productos y sus IDs
    df, product_ids = get_product_features_from_db()

    # Paso 2: Normalizar los datos
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)

    # Paso 3: Aplicar KMeans para clustering
    kmeans = KMeans(n_clusters=5, random_state=42)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    # Obtener conteo de favoritos por producto
    favorite_counts = FavoriteProduct.objects.values('product').annotate(count=Count('id'))

    # Convertir a diccionario para acceso rápido
    favorite_dict = {str(item['product']): item['count'] for item in favorite_counts}

    # Añadirlo a df como columna
    df['popularity_score'] = product_ids.map(favorite_dict).fillna(0).astype(int)
    df['product_id'] = product_ids

    # Seleccionar los 6 más populares
    top_recommendations = df.sort_values('popularity_score', ascending=False).head(6)
    return top_recommendations['product_id'].tolist() # o cualquier otra columna que quieras retornar
