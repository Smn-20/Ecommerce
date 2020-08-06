import json
from .models import *

def cookieCard(request):
    try:
        card=json.loads(request.COOKIES['card'])
    except:
        card={}
    print("Card:",card)
    items=[]
    order={'get_card_items':0,'get_card_total':0,'shipping':False}
    cardItems=order['get_card_items']
    for i in card:
        try:
            cardItems+=card[i]['quantity']
            product=Product.objects.get(id=i)
            total=(product.price*card[i]['quantity'])
            order['get_card_total']+=total
            order['get_card_items']+=card[i]['quantity']
            item={
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL,
                },
                'quantity':card[i]['quantity'],
                'get_total':total,
            }
            items.append(item)
            if product.digital==False:
                order['shipping']=True
        except:
            pass

    return {'cardItems':cardItems,'order':order,'items':items}

def cardData(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cardItems=order.get_card_items
    else:
        cookieData=cookieCard(request)
        cardItems=cookieData['cardItems']
        order=cookieData['order']
        items=cookieData['items']
    return {'cardItems':cardItems,'order':order,'items':items}

def guestOrder(request,data):
    print('User is not logged in..')
    print('COOKIES:',request.COOKIES)
    name=data['form']['name']
    email=data['form']['email']
    cookieData=cookieCard(request)
    items=cookieData['items']
    customer,created=Customer.objects.get_or_create(email=email)
    customer.name=name
    customer.save()
    order=Order.objects.create(
        customer=customer,
        complete=False,
    )
    for item in items:
        product=Product.objects.get(id=item['product']['id'])
        orderItem=OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
            )
    return customer,order