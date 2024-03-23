from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from store.pagination import DefaultPagination
from rest_framework.response import Response
from rest_framework import status
from store.filters import ProductFilter
from store.permisssions import IsAdminOrReadOnly, ViewCustomerHistoryPermission
from .models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection, ProductImage, Review
from .serializer import AddCartItemSerializer, CartItemSerializer, CartSerializer, CollectionSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductImageSerializer, ProductSerializer, ReviewSerializer, UpdateCartItemSerializer, UpdateOrderSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin 
#ViewSet

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields=['collection_id']
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title','description'] 
    ordering_fields = ['unit_price', 'last_update']
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response( {'error':'Product cannot be deleted because it is associated with order'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
            products_count=Count('product'))
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    # def delete(self, request, pk):
    #     collection =  get_object_or_404(Collection, pk=pk)
    #     if collection.products.count() > 0:
    #         return Response( {'error':'Product cannot be deleted because it is associated with order'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     collection.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    
class CartViewSet(CreateModelMixin, 
                  RetrieveModelMixin, 
                  DestroyModelMixin, 
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all() #prefetch items and product both
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete'] #must be lowercase

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        return CartItem.objects\
            .filter(cart_id=self.kwargs['carts_pk'])\
            .select_related('product')

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['carts_pk']}

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('ok')
  
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAuthenticated()]
 
    @action(detail=False, methods=['GET','PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        #if user not logged in, it gives AnonymousUser
        (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)

        if request.method=='GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    #overriding this one
    #returned only cart item
    #it will not return cart item and orders
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
                        data=request.data, 
                        context = {'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        print(' i am in serializer of OrderViewSet')
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        print('get queryset OrderViewSet')
        if user.is_staff:
            return Order.objects.all()
        
        (customer_id, created) = Customer.objects.only('id').get_or_create(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['products_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['products_pk']}