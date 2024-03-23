from django.urls import path
from . import views
from pprint import pprint
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet, basename='collections')
#pprint(router.urls)

router.register('carts',views.CartViewSet)
router.register('customers',views.CustomerViewSet)
router.register('orders',views.OrderViewSet, basename='orders')
# pprint(router.urls)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='products')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews-detail')
#basename is used as prefix for generating url pattern
products_router.register('images', views.ProductImageViewSet, basename='product-images')
#pprint(products_router.urls)

carts_router = routers.NestedDefaultRouter(router, 'carts',lookup='carts')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')
#pprint(carts_router.urls)

urlpatterns = router.urls + products_router.urls + carts_router.urls
 
# urlpatterns = [
#     path('products/', views.ProductList.as_view()),
#     path('products/<int:pk>/', views.ProductDetail.as_view()),
#     # path('collections/<int:pk>/', views.collection_detail, name='collection-detail')
#     # path('collections/', views.CollectionList.as_view()), 
#     # path('collections/<int:pk>/', views.CollectionDetail.as_view(),name='collection-detail'),
# ]