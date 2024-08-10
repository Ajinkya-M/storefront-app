from django.urls import path
from . import views, rest_views, cart_rest_views
from rest_framework.routers import SimpleRouter
from django.urls import include
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register('rest/products', rest_views.ProductViewSet)
router.register('rest/collections', rest_views.CollectionViewSet)
router.register('rest/reviews', rest_views.ReviewViewSet)
router.register('rest/carts', cart_rest_views.CartViewSet)

cart_router = routers.NestedDefaultRouter(router, 'rest/carts', lookup='cart')
cart_router.register('cartitems', cart_rest_views.CartItemViewSet, basename='cartitems')


# url conf

urlpatterns = [
    path('', include(router.urls)),
    path('', include(cart_router.urls)),
    path('rest/products/<int:pk>/reviews/', rest_views.ProductReviewList.as_view()),
    path('rest/products/<int:product_id>/reviews/<int:pk>', rest_views.ProductReviewDetails.as_view(), name='review-details'),
    # path('rest/carts/<int:cart_id>/cartitems/', cart_rest_views.CartItemList, name='cartitem-list')
]


# urlpatterns = router.urls
# urlpatterns = [
#     path('hello/', views.hello),
#     path('world/', views.world),
#     path('anno/', views.annotation),
#     path('hello_json/', view=views.hello_json),
#     path('category-sale/', views.categoty_sale),
#     path('rest/products/', rest_views.ProductList.as_view()),
#     path('rest/products/<int:pk>', rest_views.ProductDetails.as_view()),
#     path('rest/collections/<int:pk>', rest_views.CollectionDetails.as_view(), name='collection-detail'),
#     path('rest/collections/', rest_views.CollectionList.as_view(), name='collection-list'),
# ]
