from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from datetime import datetime
from salesRecord.models import Sale
from pyecharts.charts import Bar
from pyecharts import options as opts
from rest_framework.decorators import api_view
from userAcessJWT.models import CustomUser
from django.utils import timezone
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from sgeStore.decorators import role_required

@role_required('user')
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
    time_periods = [entry['time_period'].strftime('%Y-%m-%d') for entry in total_sales_data]
    total_sales = {period['time_period'].strftime('%Y-%m-%d'): float(period['total_sales']) for period in total_sales_data}

    # Preparar os dados para a linha de "Renda por Seller"
    seller_sales_data = (
        sales.values('time_period', 'seller')
        .annotate(total_sales=Sum('total_price'))
        .order_by('time_period', 'seller')
    )

    sellers = set(entry['seller'] for entry in seller_sales_data)  # Lista de vendedores únicos
    seller_sales_dict = {seller: {} for seller in sellers}

    for entry in seller_sales_data:
        period = entry['time_period'].strftime('%Y-%m-%d')
        seller = entry['seller']
        seller_sales_dict[seller][period] = float(entry['total_sales'])

    # Populate seller_lines with sales or 0 for each time period
    seller_lines = {seller: [] for seller in sellers}
    for seller in sellers:
        for period in time_periods:
            seller_lines[seller].append(seller_sales_dict[seller].get(period, 0))

    # Verify that the sum of seller sales matches total_sales for each period
    for i, period in enumerate(time_periods):
        seller_sum = sum(seller_lines[seller][i] for seller in sellers)
        if seller_sum != total_sales[period]:
            print(f"Mismatch in period {period}: Total={total_sales[period]}, Sellers sum={seller_sum}")

    # Prepare total_sales list in the same order as time_periods
    total_sales_list = [total_sales.get(period, 0) for period in time_periods]

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
            "data": ["Renda Bruta"] + list(sellers)  # Adiciona a "Renda Bruta" e os vendedores
        },
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
                "data": total_sales_list,
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
@role_required('user')
@api_view(['GET'])
def daily_sales(request):
    # Get today's date
    today = timezone.now().date()
    
    # Filter sales for today
    sales_today = Sale.objects.filter(sale_date__date=today)
    
    # Calculate total sales
    total_sales = sales_today.aggregate(total=Sum('total_price'))
    total = total_sales['total'] or 0  # Default to 0 if no sales
    
    # Prepare response data
    data = {
        'date': today.strftime('%Y-%m-%d'),
        'total_sales': float(total)
    }
    
    # Return JSON response
    return JsonResponse(data)