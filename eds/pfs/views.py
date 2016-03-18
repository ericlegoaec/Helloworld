from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from pfs.models import Portfolio, Trade, Price, Relatename
import datetime
import csv

# Create your views here.
def index(request):
    uname = None
    if request.user.is_authenticated():
        uname = request.user.username

    # pf_id = NULL
    # if request.method == 'GET':
    #     if request.GET['pf_id']:
    #         pf_id = request.GET['pf_id']

    #! Return Portfolio and Trade
    portfolio_list = Portfolio.objects.all()
    trade_list = Trade.objects.all()
    # return render_to_response('pfs/index.html', 
    #     {'uname': uname, 'portfolio_list': portfolio_list, 'trade_list': trade_list})
    
    pf_name_list = []
    for r in Portfolio.objects.all():
        if r.pf_id not in pf_name_list:
            pf_name_list.append(r.pf_id)

    pf_list = []
    for pf_id in pf_name_list:
        r = dict()        
        portfolio_list = get_pf_detail(pf_id)

        capital_sum = 0.000001
        pal_sum = 0
        mtd_sum = 0
        inception_sum = 0
        leverage = 2.0

        print portfolio_list

        for stock in portfolio_list:
            if stock['capital']:
                capital_sum = capital_sum + stock['capital']
            if stock['pal']:
                pal_sum = pal_sum + stock['pal']
            if stock['mtd']:
                mtd_sum = pal_sum + stock['mtd']
            if stock['inception']:
                inception_sum = inception_sum + stock['inception']

        r['pf_id'] = pf_id
        r['pal'] = pal_sum/capital_sum/leverage
        r['mtd'] = mtd_sum/capital_sum/leverage
        r['inception'] = inception_sum/capital_sum/leverage

        pf_list.append(r)

    print pf_list

    return render_to_response('pfs/index.html', 
         {'uname': uname, 'pf_id': None, 'pf_list': pf_list, 'portfolio_list': portfolio_list, 'trade_list': trade_list})

def stock_yeild(pf_id, stock, begin_date, end_date):    
    print begin_date, end_date
    stock_last_date = Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock, date__lte = end_date).latest('date').date    
    if begin_date and stock_last_date <= begin_date:   
        return None
    try:
        establish_date = Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock ).order_by('date')[0].date
        if begin_date:
            if Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock, date__lte = begin_date ).count() == 1:
                stock_begin_date = Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock, date__lte = begin_date ).latest('date').date
            else:
                stock_begin_date = establish_date
        else:
            stock_begin_date = establish_date
    except:
        return None

    if stock_begin_date >= stock_last_date:
        return None

    print stock, stock_begin_date, stock_last_date
    
    stock_cost = Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock, date__exact = establish_date)[0].stock_sum
    cost1 = stock_cost + Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock, date__exact = stock_begin_date)[0].app_fee
    cost2 = stock_cost + Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock, date__exact = stock_last_date)[0].app_fee

    # portfolio_list.append(Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock, date__exact = stock_last_date)[0])
    Q1 = Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock, date__exact = stock_begin_date)[0].quantity
    Q2 = Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock, date__exact = stock_last_date)[0].quantity

    price_query_set = Price.objects.filter(stock_id__exact = stock, date__exact = stock_begin_date)
    if price_query_set.count() == 1:
        P1 = price_query_set[0].price
    else: 
        return None

    price_query_set = Price.objects.filter(stock_id__exact = stock, date__exact = stock_last_date)
    if price_query_set.count() == 1:
        P2 = price_query_set[0].price
    else:
        return None

    return (cost2 + Q2*P2 - cost1 - Q1*P1)

def get_pf_detail(pf_id):
    stocknames = []
    for r in Portfolio.objects.filter(pf_id__exact = pf_id):
        if r.stock_id not in stocknames:
            stocknames.append(r.stock_id)

    portfolio_list = []
    for stock in stocknames:
        stock_last_date = Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock).latest('date').date
        # stock_begin_date = Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock).order_by('date')[0].date
        r = dict()
        r['stock_id'] = stock
        r['name'] = None
        r['sector'] = None
        r['industry'] = None
        r['quantity'] = Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock, date__exact = stock_last_date)[0].quantity
        r['direction'] = "L" if r['quantity'] > 0 else "S"

        r['price'] = None
        price_query_set = Price.objects.filter(stock_id__exact = stock, date__exact = datetime.date.today())
        if price_query_set.count() == 1:
            r['price'] = price_query_set[0].price
        # print 'Hello', price_query_set.count()

        r['capital'] = None
        r['pal'] = None
        r['palp'] = None 
        price_yesterday = None
        price_query_set = Price.objects.filter(stock_id__exact = stock, date__exact = datetime.date.today() - datetime.timedelta(1))
        if price_query_set.count() == 1:
            price_yesterday = price_query_set[0].price
            r['capital'] = r['quantity'] * price_yesterday
            r['pal'] = r['quantity'] * (r['price'] - price_yesterday)
            r['palp'] = r['pal'] / abs(r['capital'])
        
        today = datetime.date.today()
        r['mtd'] = stock_yeild(pf_id, stock, datetime.date(day=1, month=today.month, year=today.year)-datetime.timedelta(1), datetime.date.today())
        r['inception'] = stock_yeild(pf_id, stock, None, datetime.date.today())

        portfolio_list.append(r)

    return portfolio_list

def pf_detail(requst, pf_id):
    portfolio_list = get_pf_detail(pf_id)
    # pf_id = get_object_or_404(Portfolio, pk=pf_id)
    return render_to_response('pfs/index.html', 
        {'uname': 'test', 'pf_id': pf_id, 'portfolio_list': portfolio_list} )

@csrf_exempt
@login_required
def date_querry(request):
    if request.method == 'POST':
        if request.POST['dp']:
            dp = request.POST['dp']
            print dp, type(dp)
    return render_to_response('pfs/index.html', {'uname': dp})

@csrf_exempt
@login_required
def pf_update(request):
    status = -1
    if request.method == 'POST':
        file = request.FILES.get('pfInputFile', False)
        if not file:
            status_info = "You should upload the CSV file!";
            return render_to_response('pfs/uploads.html', {'status': status, 'status_info': status_info})

        if file.name.split(".")[-1] != "csv":
            status_info = "The upload file type should be CSV!"
            return render_to_response('pfs/uploads.html', {'status': status, 'status_info': status_info})

        data = [row for row in csv.reader(file.read().splitlines())]
        # data validation (pf_id, bbcode, Quantity, date)
        # ... to be done!

        # 1. Delete all pf_id related items
        pf_name_dict = {}
        pf_date_dict = {}
        for i in range(1, len(data)):
            pf_id = data[i][0]
            # translate the date format
            d = data[i][3].split('/')
            data[i][3] = datetime.date(int(d[0]), int(d[1]), int(d[2]))
            if pf_id not in pf_name_dict:
                pf_name_dict[pf_id] = 1
                pf_date_dict[pf_id] = data[i][3]
            else:
                pf_name_dict[pf_id] = pf_name_dict[pf_id] + 1

        for pf_id in pf_name_dict:
            Portfolio.objects.filter(pf_id__exact = pf_id).delete()

        # 2. Update Portfolio model (The first day) 
        for i in range(1, len(data)):
            pf_id = data[i][0]
            stock_id = data[i][1]
            quantity = int(data[i][2])
            date = data[i][3]
            price = float(data[i][4])
            stock_sum = quantity * price
            member = Portfolio.objects.create(pf_id = pf_id, stock_id = stock_id, quantity = quantity, 
                date = date, price = price, stock_sum = quantity*price, app_fee = 0)
            member.save()

        # 3. Update Portfolio model (The following days), refer to Trade model corrosponding to each pf_id        
        for pf_id in pf_name_dict:
            date = pf_date_dict[pf_id]
            # Track stocks in a portfolio
            stock_app_dict = {}
            stock_quantity_dict = {}
            T = Trade.objects.filter(pf_id = pf_id, date__gt = date).order_by('date')
            for t in T:
                stock_id = t.stock_id
                # First time in 
                if stock_id not in stock_app_dict:
                    stock_app_dict[stock_id] = 0
                    stock_quantity_dict[stock_id] = Portfolio.objects.filter(pf_id__exact = pf_id, stock_id__exact = stock_id)[0].quantity

                stock_app_dict[stock_id] = stock_app_dict[stock_id] - t.price*t.quantity
                stock_quantity_dict[stock_id] = stock_quantity_dict[stock_id] + t.quantity

                quantity = stock_quantity_dict[stock_id]
                date = t.date
                app_fee = stock_app_dict[stock_id]
                member = Portfolio.objects.create(pf_id = pf_id, stock_id = stock_id, quantity = quantity, 
                    date = date, price = 0, stock_sum = 0, app_fee = app_fee)
                member.save()

        status = 1
        status_info = "Ok, the " + file.name + " has been uploaded!"
        return render_to_response('pfs/uploads.html', {'status': status, 'status_info': status_info})

    if request.method == 'GET':
        return render_to_response('pfs/uploads.html')

@csrf_exempt
@login_required
def trade_update(request):
    status = -10
    if request.method == 'POST':
        file = request.FILES.get('tradeInputFile', False)
        if not file:
            status_info = "You should upload the CSV file!";
            return render_to_response('pfs/uploads.html', {'status': status, 'status_info': status_info})

        if file.name.split(".")[-1] != "csv":
            status_info = "The upload file type should be CSV!";
            return render_to_response('pfs/uploads.html', {'status': status, 'status_info': status_info})

        data = [row for row in csv.reader(file.read().splitlines())]
        # data validation (pf_id, bbcode, Quantity, date)
        # ... to be done!

        # Update data into the Trade Model
        pf_dates_dict = {} 
        # Info:
        #   pf_date_dict (dict)
        #   Key: pf_id (string)
        #   Value: date (list)
        for i in range(1, len(data)):
            pf_id = data[i][0]
            stock_id = data[i][1]
            side = data[i][2]
            quantity = int(data[i][3])
            date = data[i][4]
            d = date.split('/')
            date = datetime.date(int(d[0]), int(d[1]), int(d[2]))
            price = float(data[i][5])

            if pf_id not in pf_dates_dict:
                pf_dates_dict[pf_id] = []
            else:
                if date not in pf_dates_dict[pf_id]:
                    pf_dates_dict[pf_id].append(date)

            if side == 'B':
                quantity = quantity
            elif side == 'S':
                quantity = -quantity
            elif side == 'SS':
                quantity = -quantity

            member = Trade.objects.create(pf_id = pf_id, stock_id = stock_id, quantity = quantity, date = date, price = price)
            member.save()

        for pf_id in pf_dates_dict:
            pf_dates_dict[pf_id].sort()
            date = pf_dates_dict[pf_id][0]

            # Only Save Trade File
            if Portfolio.objects.filter(pf_id__exact = pf_id, date__lte = date).count() == 0:
                continue

            last_date = Portfolio.objects.filter(pf_id__exact = pf_id, date__lte = date).latest('date').date

            # Delete all items in Portfolio from the trade date
            Portfolio.objects.filter(pf_id__exact = pf_id, date__gte = date).delete()

            # Track stocks in a portfolio from the earlist trading date
            stock_app_dict = {}
            stock_quantity_dict = {}
            P = Portfolio.objects.filter(pf_id__exact = pf_id, date__exact = last_date)
            for p in P:
                stock_id = p.stock_id
                stock_app_dict[stock_id] = p.app_fee
                stock_quantity_dict[stock_id] = p.quantity
    
            T = Trade.objects.filter(pf_id = pf_id, date__gt = last_date).order_by('date')
            for t in T:
                stock_id = t.stock_id

                stock_app_dict[stock_id] = stock_app_dict[stock_id] - t.price*t.quantity
                stock_quantity_dict[stock_id] = stock_quantity_dict[stock_id] + t.quantity

                quantity = stock_quantity_dict[stock_id]
                app_fee = stock_app_dict[stock_id]
                date = t.date
                member = Portfolio.objects.create(pf_id = pf_id, stock_id = stock_id, quantity = quantity, 
                    date = date, price = 0, stock_sum = 0, app_fee = app_fee)
                member.save()

        status = 10
        status_info = "Ok, the " + file.name + " has been uploaded!"
        return render_to_response('pfs/uploads.html', {'status': status, 'status_info': status_info})

    if request.method == 'GET':
        return render_to_response('pfs/uploads.html')
