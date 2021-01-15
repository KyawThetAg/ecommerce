from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cartData, cookieCart, guestOrder



def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    order = data['order']
    
    products = Product.objects.all()
    context = {
        'products': products,
        'cartItems': cartItems
    }
    return render(request, 'store/store.html', context)

def product_detail(request, id):
    products = Product.objects.get(id=id)
    context = {
        'products': products,
    }
    return render(request, 'store/single.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    order = data['order']
            
    context = {'items': items, 'order': order, 'cartItems': cartItems, 'shipping': False}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    order = data['order']
    
    context = {'items': items, 'order': order, 'cartItems': cartItems, 'shipping': False}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productid = data['productId']
    action = data['action']
    
    customer = request.user.customer
    product = Product.objects.get(id=productid)
    order, create = Order.objects.get_or_create(customer=customer, complete=False)
    
    orderItem, create = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    
    if orderItem.quantity < 1:
        orderItem.delete()
        
    return JsonResponse('It was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, create = Order.objects.get_or_create(customer=customer, complete=False)
        
    else:
        customer, order = guestOrder(request, data)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()
    
    if order.shipping == True:
        ShoppingAddress.objects.create(
        customer = customer,
        order = order,
        address = data['shipping']['address'],
        city = data['shipping']['city'],
        state = data['shipping']['state'],
        zipcode = data['shipping']['zipcode'],
    )
    return JsonResponse('Payment complete!', safe=False)
