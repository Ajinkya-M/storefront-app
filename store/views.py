from decimal import Decimal
from django.shortcuts import render
from django.db.models import Q, F, ExpressionWrapper, DecimalField
from django.http import HttpResponse, JsonResponse
from .models import Product, Collection, Customer, OrderItem, Order, Cart, CartItem
from django.db.models.aggregates import Count, Min, Max, Avg, Sum
from django.http import HttpResponse

# Create your views here.
def hello_json(request):
    print('hello end point hit...')
    products = []
    query_set = Product.objects.select_related(Collection.name)
    for product in query_set:
        products.append({
            'name': product.name,
            'description': product.description,
            'price': product.price
        })

    return JsonResponse({'products': products}, safe=False)


def hello_world(request):
    one = Customer.objects.filter(email__icontains='.com')
    print(list(one))

    two = Collection.objects.filter(featured_product__isnull=True)
    print(f'collections with no fetured product : {list(two)}')

    three = Product.objects.filter(inventory__lt=10)
    print(three)

    four = Order.objects.filter(customer__id=1)
    print(four)

    five = OrderItem.objects.filter(product__collection__title__in=('Grocery', 'Beauty', 'Cleaning')).filter(
        order__customer__email__contains='.com')
    print(five)

    six = Product.objects.filter(collection__title='Grocery')
    print(six)

    return render(request, 'hello.html', {'products': [], })


def world(request):
    one = Product.objects.filter(unit_price__range=(20, 30)).filter(
        Q(collection__title='Grocery') | Q(collection__title='Beauty'))
    print(list(one))

    two = Product.objects.filter(title=F('collection__title'))
    print(list(two))

    two = Product.objects.order_by('-unit_price', '-title')
    print(list(two))
    return render(request, 'hello.html', {'products': []})


def hello(request):
    # prod_ids_qset = OrderItem.objects.values('product_id').distinct()
    # prods = Product.objects.filter(id__in=prod_ids_qset).order_by('title')
    # query_set = Product.objects.select_related('collection').prefetch_related('promotions').all()
    # order_customer = OrderItem.objects.select_related('product__collection').filter(product__collection__title__icontains='Beauty')
    # print(order_customer)
    # last5 = Order.objects.select_related('customer').order_by('-placed_at')[:5]
    # last = OrderItem.objects.filter(order_id__in=Order.objects.order_by('-placed_at')[:5]).select_related('order__customer', 'product').all()
    # print(last)
    # collection_set = Collection.objects.prefetch_related('product_set').all()
    # for collection in collection_set:
    #     print(collection.title, '-------------------------------')
    #     for product in collection.product_set.all():
    #         print('   |-', product.title, product.unit_price)

    latest_orders = Order.objects.select_related('customer').prefetch_related('orderitem_set',
                                                                              'orderitem_set__product').order_by(
        '-placed_at')[:5]
    
    result  = Product.objects.aggregate(count=Count('id'), min_price=Min('unit_price'))

    orders = Order.objects.aggregate(Count('id'))
    prod_1_sold = Product.objects.filter(id=1).prefetch_related('orderitem_set').aggregate(Sum('orderitem__quantity'))
    prod_1_sold_alt = OrderItem.objects.filter(product_id=1).aggregate(qty=Sum('quantity'))
    print(f'orders : {orders} | prod 1 sold : {prod_1_sold}, alt : {prod_1_sold_alt}')

    customer_1_placed_orders = Customer.objects.filter(id=1).prefetch_related('order_set').aggregate(Count('order__id'))
    print(f'customer 1 placed  : {customer_1_placed_orders}')    

    collection_3_stats = Product.objects.filter(collection_id=3).aggregate(min=Min('unit_price'), max=Max('unit_price'), avg=Avg('unit_price'))
    print(f'collection stats ; {collection_3_stats}')
    return render(request, 'hello.html', {'orders': list(latest_orders)})


def annotation(request):
    result_1 = Customer.objects.annotate(
        last_order=Max('order__id')
    )
    print(result_1)

    result_2 = Collection.objects.annotate(
        product_count=Count('product')
    )
    print(result_2)

    result_3 = Customer.objects.annotate(
        order_count=Count('order')
    ).filter(order_count__gt=5)
    print(result_3)

    cost = ExpressionWrapper(
            F('order__orderitem__product__unit_price') * F('order__orderitem__quantity'), 
            DecimalField(max_digits=6, decimal_places=2)
        )

    customer_spend = Customer.objects.annotate(
        amount_spent=Sum(cost)
    ).filter(amount_spent__gt=0).values('id', 'first_name', 'amount_spent')
    print(customer_spend[:40])

    sale = ExpressionWrapper(F('orderitem__quantity') * F('unit_price'), DecimalField())
    top_5_products = Product.objects.annotate(
        total_sale=Sum(sale),
        units_sold=Sum(F('orderitem__quantity'))
    ).order_by('-total_sale')[:5]
    print(top_5_products)

    # print(f'product with id - 1 : {Product.objects.get(pk=1)}')
    # Collection.objects.filter(pk=1).update(featured_product=None)
    # Collection.objects.filter(pk=1).update(featured_product=Product.objects.get(pk=1))


    # CartItem.objects.filter(pk=1).update(quantity=12)
    Cart.objects.filter(pk=1).delete()



    return render(request, 'hello.html', {'customers': customer_spend})


def categoty_sale(request):
    total_sale = ExpressionWrapper(
        F('product__orderitem__quantity') *
        F('product__unit_price'),
        DecimalField()
    )
    queryset = Collection.objects.values('title').annotate(
        total_sale=Sum(total_sale),
        total_orders=Count(F('product__orderitem__quantity'))
        ).order_by('-total_sale')

    return render(request, 'hello.html', {'sale': list(queryset)})



def product_list(request):
    return HttpResponse('ok')