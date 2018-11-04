from django.shortcuts import render, HttpResponse

# Create your views here.


def main_pg(request):
    print('market')
    return render(request, 'market/market_main_pg.html')


def customers(request):
    """
    浏览客户信息
    :param request:
    :return:
    """
    pass


def customers_modify(request, nid):
    """
    修改客户信息
    :param request:
    :param nid: 要修改的客户ID
    :return:
    """


def enrollment(request, nid):
    """
    帮助客户完成注册成为学员
    :param request:
    :param nid: 要注册的客户ID
    :return:
    """
    print("nothing")
