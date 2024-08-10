from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from .models import Product, Collection, Review
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from pprint import pprint



class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {'request' : self.request}
    
    def destroy(self, reqeust, pk: int):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitem_set.count() > 0:
            return Response(
                {'error': 'method not allowed as product is associated with order item.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('product'))

    serializer_class = CollectionSerializer

    def get_serializer_context(self):
        return {'request' : self.request}
    
    def destroy(self, request, pk: int,  *args, **kwargs):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.product_set.count() > 0:
            return Response({'error' : 'collection deletion not allowed as product associated with it'}, 
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        return {'request' : self.request}


class ProductList(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {'request' : self.request}
    
    

class ProductReviewList(ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs['pk']
        return Review.objects.filter(product_id=product_id)
    
    def perform_create(self, serializer):
        product_id = self.kwargs['pk']
        product = get_object_or_404(Product, pk=product_id)
        serializer.save(product=product)


class ProductReviewDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id)
    

        


@api_view()
def product_review_list(request, pk: int):
    review_queryset = Review.objects.filter(product_id=pk).all()
    serializer = ReviewSerializer(review_queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# class ProductList(APIView):
#     def get(self, request):
#         products_query_set = Product.objects.select_related('collection').all().order_by('-last_update')
#         serializer = ProductSerializer(
#             products_query_set, 
#             many=True, 
#             context={'request': request}
#             )
#         return Response(serializer.data)
    
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         saved_product = serializer.save()
#         print(saved_product)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetails(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def delete(self, reqeust, pk: int):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitem_set.count() > 0:
            return Response(
                {'error': 'method not allowed as product is associated with order item.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class ProductDetails(APIView):
#     def get(self, request, id: int):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
#     def put(self, request, id: int):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#     def patch(self, request, id: int):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#     def delete(self, reqeust, id: int):
#         product = get_object_or_404(Product, pk=id)
#         if product.orderitem_set.count() > 0:
#             return Response(
#                 {'error': 'method not allowed as product is associated with order item.'},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED
#             )
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(
        products_count=Count('product')
    ).all()

    serializer_class = CollectionSerializer

    def get_serializer_context(self):
        return {'request' : self.request}
    


class CollectionDetails(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(
        products_count=Count('product')
    ).all()
    serializer_class = CollectionSerializer

    def delete(self, request, pk: int,  *args, **kwargs):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.product_set.count() > 0:
            return Response({'error' : 'collection deletion not allowed as product associated with it'}, 
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products_query_set = Product.objects.select_related('collection').all().order_by('-last_update')
        serializer = ProductSerializer(
            products_query_set, 
            many=True, 
            context={'request': request}
            )
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved_product = serializer.save()
        print(saved_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def product_details(request, id: int):
    product = get_object_or_404(Product, pk=id)
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    elif request.method == 'DELETE':
        if product.orderitem_set.count() > 0:
            return Response(
                {'error': 'method not allowed as product is associated with order item.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def collection_details(request: Request, pk: int):
    collection = get_object_or_404(Collection.objects.annotate(
                                            products_count = Count('product')
                                        ), 
                                   pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        if collection.product_set.count() > 0:
            return Response({'error' : 'collection deletion not allowed as product associated with it'}, 
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == 'GET':
        # collection_query_set = Collection.objects.prefetch_related('product_set').order_by('id').all()
        collection_query_set = Collection.objects.annotate(
            products_count = Count('product')
        ).all()
        serialiser = CollectionSerializer(collection_query_set, many=True)
        return Response(serialiser.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serialiser = CollectionSerializer(data=request.data)
        serialiser.is_valid(raise_exception=True)
        serialiser.save()
        return Response(serialiser.data, status=status.HTTP_201_CREATED)
    
