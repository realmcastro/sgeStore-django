from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from datetime import datetime
from salesRecord.models import Sale
from pyecharts.charts import Bar
from pyecharts import options as opts
from rest_framework.decorators import api_view
from userAcessJWT.models import CustomUser
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear

@api_view(['POST'])
def sales_chart(request):
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    time_period = request.data.get('time_period', 'day')  # 'day', 'week', 'month', 'year'

    sales = Sale.objects.all()

    # Filtrar por data de venda, se necessário
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        sales = sales.filter(sale_date__gte=start_date)
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        sales = sales.filter(sale_date__lte=end_date)

    # Agrupar as vendas por data de acordo com o período de tempo selecionado
    if time_period == 'day':
        sales = sales.annotate(time_period=TruncDate('sale_date'))
    elif time_period == 'week':
        sales = sales.annotate(time_period=TruncWeek('sale_date'))
    elif time_period == 'month':
        sales = sales.annotate(time_period=TruncMonth('sale_date'))
    elif time_period == 'year':
        sales = sales.annotate(time_period=TruncYear('sale_date'))

    # Agregar as vendas por período de tempo
    total_sales_data = (
        sales.values('time_period')
        .annotate(total_sales=Sum('total_price'))
        .order_by('time_period')
    )

    # Preparar os dados para a linha de "Renda Bruta" (soma total de todas as vendas)
    total_sales = [float(entry['total_sales']) for entry in total_sales_data]
    time_periods = [entry['time_period'].strftime('%Y-%m-%d') for entry in total_sales_data]

    # Preparar os dados para a linha de "Renda por Seller"
    seller_sales_data = (
        sales.values('time_period', 'seller')
        .annotate(total_sales=Sum('total_price'))
        .order_by('time_period', 'seller')
    )

    sellers = list(set([entry['seller'] for entry in seller_sales_data]))  # Lista de vendedores únicos
    seller_lines = {seller: [] for seller in sellers}  # Dicionário para armazenar as linhas de cada vendedor

    # Preencher as linhas de vendas por vendedor
    for seller in sellers:
        seller_sales = [
            float(entry['total_sales']) if entry['seller'] == seller else 0
            for entry in seller_sales_data
        ]
        seller_lines[seller] = seller_sales

    # Criar o gráfico com ECharts
    chart_data = {
        "title": {
            "text": "Evolução das Vendas"
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c}"
        },
        "legend": {
            "data": ["Renda Bruta"] + sellers  # Adiciona a "Renda Bruta" e os vendedores
        },
        # "toolbox": {
        #     "show": True,
        #     "feature": {
        #         "mySwitch": {
        #             "show": True,
        #             "title": "Alternar",
        #             "icon": "path://M16 10H8V2H16ZM6 18H8V12H6ZM16 18H14V12H16Z",  # Ícone de alternância
        #             "onclick": "function () { mySwitchFunction(); }"
        #         }
        #     }
        # },
        "xAxis": {
            "type": "category",
            "data": time_periods
        },
        "yAxis": {
            "type": "value"
        },
        "series": [
            {
                "name": "Renda Bruta",  # Linha para a renda bruta
                "type": "line",
                "data": total_sales,
                "id": "total_sales"  # Identificador da série
            }
        ] + [
            {
                "name": seller,  # Linha para cada vendedor
                "type": "line",
                "data": seller_lines[seller],
                "id": seller  # Identificador da série
            }
            for seller in sellers
        ]
    }

    return JsonResponse(chart_data, safe=False)

