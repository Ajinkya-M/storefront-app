from rest_framework import serializers
from .models import Product, Collection, Review, Cart, CartItem
from decimal import ROUND_DOWN, Decimal

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
        
    products_count = serializers.IntegerField(read_only=True) 

    # def get_products_count(self, collection: Collection):
    #     return collection.product_set.count()
        

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'unit_price', 'inventory', 'price_with_tax', 'collection']


    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    # unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    price_with_tax = serializers.SerializerMethodField()
    # collection = serializers.PrimaryKeyRelatedField(
    #     queryset=Collection.objects.all()
    # )
    # collection = CollectionSerializer()
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(),
    #     view_name='collection-detail'
    # )

    def get_price_with_tax(self, product: Product):
        return (product.unit_price * Decimal(1.1)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    
    
class ReviewHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'product_id': obj.product_id,
            'pk': obj.pk
        }
        return self.reverse(view_name, kwargs=url_kwargs, request=request, format=format)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'review_text', 'product', 'date', 'review']
        read_only_fields = ['product', 'date'] 

    review = ReviewHyperlinkedIdentityField(view_name='review-details')

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = CartItem
        fields = ['id', 'cart_id', 'product', 'quantity', 'total_price']
        read_only_fields = ['cart_id']

    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cartItem: CartItem):
        return cartItem.quantity * cartItem.product.unit_price


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f'No Product with id:{value} exists')
        return value

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']     

    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']
        try:
            # update item
            cartitem = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cartitem.quantity += quantity
            cartitem.save()
            self.instance = cartitem
        except CartItem.DoesNotExist:
            # create a new item
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        
        return self.instance
    

class UpdateCartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ['quantity']     


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'cartitem_set', 'total_price']
        read_only_fields = ['cartitem_set']

    cartitem_set = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        total_price = 0
        for cartitem in cart.cartitem_set.all():
            total_price += cartitem.quantity * cartitem.product.unit_price
        return total_price