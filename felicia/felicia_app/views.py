from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from django.shortcuts import render,get_object_or_404,redirect
from .models import Product, Order, OrderUpdate, Category, SubCategory, Contact
from django.contrib.auth import authenticate
from rest_framework.generics import ListAPIView
from .serializers import PriceSerializers
from .pagination import StandardResultsSetPagination1
import ast
from django.forms.models import model_to_dict

# Create your views here.
from django.core.mail import send_mail
from django.conf import settings
from math import ceil
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
# from Paytm import checksum
from Paytm.checksum import *


from django.conf import settings
import os

MERCHANT_KEY = os.getenv("PAYTM_MERCHANT_KEY", "")
PAYTM_MID = os.getenv("PAYTM_MID", "")
PAYTM_WEBSITE = os.getenv("PAYTM_WEBSITE", "WEBSTAGING")
PAYTM_CALLBACK_URL = os.getenv("PAYTM_CALLBACK_URL", "http://127.0.0.1:8000/handlerequest/")



# view for Filter 
def PriceList(request):
    return render(request, "price.html",{})


class PriceListing(ListAPIView):
    # set the pagination and serializer class

    pagination_class = StandardResultsSetPagination1
    serializer_class = PriceSerializers

    def get_queryset(self):
        # filter the queryset based on the filters applied

        queryList = Product.objects.all()
        product_name = self.request.query_params.get('product_name', None)
        price = self.request.query_params.get('price', None)
        sort_by = self.request.query_params.get('sort_by', None)

        if price:
            queryList = queryList.filter(price=price)
        if product_name:
            queryList = queryList.filter(product_name=product_name)

            # sort it if applied on based on price/points

        if sort_by == "price":
            queryList = queryList.order_by("price")
        elif sort_by == "product_name":
            queryList = queryList.order_by("product_name")
        return queryList


def getPrice(request):
    # get all the countreis from the database excluding
    # null and blank values

    if request.method == "GET" and request.is_ajax():
        price = Product.objects.exclude(price__isnull=True).exclude(price=0).order_by('price').values_list('price').distinct()
        # price = Product.objects.exclude(price__isnull=True).filter(id__in='').order_by('price').values_list('price').distinct()

        price = [i[0] for i in list(price)]
        data = {
            "price": price,
        }
        print(data)
        return JsonResponse(data, status=200)


def getProduct_name(request):
    if request.method == "GET" and request.is_ajax():
        # get all the varities from the database excluding
        # null and blank values

        product_name = Product.objects.exclude(product_name__isnull=True). \
            exclude(product_name__exact='').order_by('product_name').values_list('product_name').distinct()
        product_name = [i[0] for i in list(product_name)]
        data = {
            "product_name": product_name,
        }
        return JsonResponse(data, status=200)




def all_category(request):
    sub = subcategory.objects.all()
    return render(request,'test.html',{'sub':sub})

def cat_view(request):
    category1=category.objects.all()
    print(category1)
    return render(request,'category.html',{'category':category1})

def subcat(request,catid):
    sub = subcategory.objects.all()
    subc = sub.filter(category=catid)
    print(subc)
    return render(request,'subcategory.html',{'subc':subc})

def testproduct(request,subid):
    pro = Product.objects.all()
    p = pro.filter(subcategory=subid)
    return render(request,'testproduct.html',{'p':p})

def allprod(request,subid):
    if request.method == 'POST':
        pro = Product.objects.all()
        p = pro.filter(subcategory=subid)
        return render(request,'allprod.html',{'p':p})
        
@login_required
def test(request):
    allprods = []
    prod = Product.objects.all()
    n=len(prod)
    nSlides = n//4 + ceil((n/4)-(n//4))
                

    allprods.append([prod, range(1,nSlides), nSlides])

    sub = subcategory.objects.all()
    params = {'allprods':allprods,'sub':sub}

    print(sub)

    return render(request,'test.html',params)
    return redirect("login")
def home(request):
	allprods = []
	catprods =  Product.objects.values('category','id')
	cats = {item['category'] for item in catprods}
	for cat in cats:
		prod = Product.objects.filter(category=cat)
		n=len(prod)
		nSlides = n//4 + ceil((n/4)-(n//4))
		

		allprods.append([prod, range(1,nSlides), nSlides])
	params = {'allprods':allprods}
	return render(request,'home.html',params)

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        if password == cpassword:
            users= User.objects.all()
            for u in users:
                if u.username == username:
                    return render(request,'test.html',{'error':'user already existed'})
            #user not existed
            newuser = User.objects.create_user(username,email,password)#,firstname=first_name, lastname=last_name)
            newuser.is_active = False
            newuser.is_staff = False
            newuser.is_superuser = False
            newuser.save()
            #for mail verification
            newuser_id = str(newuser.id)
            link = "http://127.0.0.1:8000/activation/" + newuser_id + "/"
            message_text = "Click on following link to complete your registration\n" + link

            send_mail('Felicia',message_text,settings.EMAIL_HOST_USER,[newuser.email],fail_silently=False)
            messages.success(request, 'user registration successfully')
            return render(request,'register.html',{'info':'registration is successfully completed'})
        else:
            return render(request, "register.html",{'error':'password not matched'})
    else:
        return render(request,'register.html')

def activation(request,user_id):
    user= get_object_or_404(User,pk=user_id)
    print(user)
    if user is not None:
        user.is_active = True
        user.save()
        print("aa")
        return redirect('/login',{'info':'Account successfully ACTIVATED!'})
    else:
        return redirect('/test',{'error':'Error with activation link'})
    return render(request,'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth.login(request, user)
                return redirect('/test',{'user':user})
            else:
                return render(request,"login.html",{'error':'Your account was inactive.'})
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return render(request,"login.html",{'error':'invalid login details.'})
    else:
        return render(request, 'login.html')
def logout(request):
    auth.logout(request)
    return (request,)

def placeorder(request):
    # product = Product.objects.filter(id=myid)
    return render(request,'placeorder.html')

def invoice(request,orderid):
    order1=model_to_dict(Order.objects.filter(order_id=orderid)[0])
    order=Order.objects.filter(order_id=orderid)
    print(type(order1))
    a=dict()
    for o in order1:
        # pro=order1[o]
        # print(type(pro),type(o))
        if o == "items_json":
            a=json.loads(order1[o])
            print("aaaaa",order1[o])
            print(type(a))
    for k in a:
        b=a[k]
        for i in b:
            print(type(i),end="")
        print()

    return render(request,'invoice.html',{'order':order,'a':a})

def checkoutform(request):
    return render(request,'checkoutform.html')
def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsjson')
        name = request.POST.get('name','')
        amount = request.POST.get('amount')
        email = request.POST.get('email','')
        address = request.POST.get('address1','')+ " " + request.POST.get('address2','')
        city = request.POST.get('city','')
        phone = request.POST.get('phone','')
        state = request.POST.get('state','')
        zip_code = request.POST.get('zip_code','')
        print(items_json,name,amount,email,address,city,phone,state,zip_code)
        
        order=Order(items_json=items_json, name=name, amount=amount, email=email, address=address, city=city, phone=phone, state=state, zip_code=zip_code)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc = "The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        #return render(request, 'shop/checkout.html', {'thank':thank, 'id':id})
        #request  paytm to tansfer the amount

        param_dict = {

            'MID':'Flqaxh89929692248450',
            # 'MID':'wZPngO36424621718883',  
            'ORDER_ID':str(order.order_id),
            'TXN_AMOUNT':str(amount),
            'CUST_ID':email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
            'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = generate_checksum(param_dict, MERCHANT_KEY)
        # print("checksum",param_dict['CHECKSUMHASH'])
        # print("param",param_dict)
        return render(request, 'paytm.html', {'param_dict': param_dict}) 
    return render(request, 'checkout.html')

def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId','')
        email = request.POST.get('email','')
        try:
            order=Order.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update=OrderUpdate.objects.filter(order_id=orderId)
                updates=[]
                for item in update:
                    updates.append({'text':item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status": "success", "updates": updates, "itemsjson": order[0].items_json}, default=str)
                return HttpResponse(response)

            else:
                return HttpResponse('{"status":"noitem"}')

        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'tracker.html')
    
@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        print(i,"==I")
        print("form[i]",form[i])
        response_dict[i] = form[i]
        if i =='CHECKSUMHASH':
            checksum = form[i]
            print(checksum,form[i])
    #verify =checksum.verify_checksum(response_dict,MERCHANT_KEY,checksum)
    verify =verify_checksum(response_dict,MERCHANT_KEY,checksum)
    print(verify,"verify")
    print(response_dict['RESPCODE'] )
    print("hello")
    if verify is True:
        print("aa")
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request,'paymentstatus.html',{'response':response_dict})

# search option----------------
def searchMatch(query,item):
    print("query",query)
    print("item",item)
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    print("query",query)

    allprods = []
    catprods =  Product.objects.values('category','id')
    print("catprod",catprods)

    cats = {item['category'] for item in catprods}
    print("cats",cats)

    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        print("prodtemp",prodtemp)

        prod = [item for item in prodtemp if searchMatch(query,item )]
        print("prod",prod)

        n=len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4))
        if len(prod) != 0:
            allprods.append([prod, range(1,nSlides), nSlides])
    params = {'allprods':allprods, "msg":""}
    print("params",params)
    if len(allprods) == 0 or len(query)<4:
        params = {'msg':"please make sure to enter relevent search query"}
    return render(request, 'search.html', params)

def productView(request, myid):
    products = Product.objects.filter(id=myid)
    return render(request, 'prodview.html',{'product':products[0]})

def aboutus(request):
    return render(request,"about.html")

def contactus(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        desc = request.POST['desc']

        c = contact(name=name,email=email,subject=subject,desc=desc)
        c.save()

    return render(request,"contact.html")

def newarrivals(request):
    obj= Product.objects.filter().order_by('-id')
    print(obj)
    a=list()
    for i in range(0,5):
        a.append(obj[i])
    print(a)
    return render(request,"newarrivals.html",{'newarvls':a})





    