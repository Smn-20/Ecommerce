from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
import datetime
from .utils import cookieCard,cardData,guestOrder
# Create your views here.

def card(request):
    data=cardData(request)
    cardItems=data['cardItems']
    order=data['order']
    items=data['items']
    context={
        'items':items,
        'order':order,
        'cardItems':cardItems
    }
    return render(request,'store/card.html',context)

def store(request):
    data=cardData(request)
    cardItems=data['cardItems']
    products=Product.objects.all()
    context={
        'products':products,
        'cardItems':cardItems
    }
    return render(request,'store/store.html',context)

def checkout(request):
    data=cardData(request)
    cardItems=data['cardItems']
    order=data['order']
    items=data['items']
    context={
        'items':items,
        'order':order,
        'cardItems':cardItems
    }
    return render(request,'store/checkout.html',context)

def updateItem(request):
    data=json.loads(request.body)
    productID=data['productID']
    action=data['action']
    print('productID:',productID,'action:',action)
    customer=request.user.customer
    product=Product.objects.get(id=productID)
    order,created=Order.objects.get_or_create(customer=customer,complete=False)
    orderItem,create=OrderItem.objects.get_or_create(order=order,product=product)
    if action=='add':
        orderItem.quantity=(orderItem.quantity+1)
    elif action=='remove':
        orderItem.quantity=(orderItem.quantity-1)
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id=datetime.datetime.now().timestamp()
    data=json.loads(request.body)

    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        
    else:
        customer,order=guestOrder(request,data)
    
    total= float(data['form']['total'])
    order.transaction_id=transaction_id
    if total==order.get_card_total:
        order.complete=True
    order.save()
    if order.shipping==True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )
    return JsonResponse('Payment complete!', safe=False)
