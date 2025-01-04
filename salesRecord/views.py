from django.shortcuts import render
from sgeStore.decorators import role_required

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from stockProducts.models import Products
from userAcessJWT.models import CustomUser
from .models import Sale

@role_required('mod')
@api_view(['POST'])
def register_sale(request):
    try:
        qr_code = request.data.get('qr_code')
        quantity = int(request.data.get('quantity'))
        seller_id = request.data.get('seller')

        if not qr_code or not quantity or not seller_id:
            return Response(
                {"error": "Os campos 'qr_code', 'quantity' e 'seller' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Products.objects.get(qr_code=qr_code)
        except Products.DoesNotExist:
            return Response(
                {"error": f"Produto com QR Code '{qr_code}' não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        if product.quantity < quantity:
            return Response(
                {"error": f"Estoque insuficiente. Disponível: {product.quantity}, Solicitado: {quantity}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(id=seller_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": f"Usuário com ID '{seller_id}' não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        sale = Sale.objects.create(
            qr_code=qr_code,
            product_name=product.name,
            product_price=product.price,
            quantity=quantity,
            seller=user.username,
            total_price=quantity * product.price
        )
        sale.save()

        product.quantity -= quantity
        product.save()

        return Response(
            {"message": "Venda registrada com sucesso.",
             "sale_id": sale.id,
             "remaining_stock": product.quantity},
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {"error": f"Erro interno: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@role_required('mod')
@api_view(['POST'])
def refund_sale(request):
    try:
        sale_id = request.data.get('sale_id')
        refund_quantity = request.data.get('refund_quantity')

        if not sale_id or refund_quantity is None:
            return Response(
                {"error": "Os campos 'sale_id' e 'refund_quantity' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refund_quantity = int(refund_quantity)  # Converte para inteiro
        except ValueError:
            return Response(
                {"error": "O campo 'refund_quantity' deve ser um número inteiro."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sale = Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            return Response(
                {"error": f"Venda com ID '{sale_id}' não encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

        if sale.refund:
            return Response(
                {"error": "Esta venda já foi reembolsada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if refund_quantity > sale.quantity:
            return Response(
                {"error": f"Quantidade de reembolso não pode ser maior que a quantidade vendida. Vendido: {sale.quantity}, Reembolsar: {refund_quantity}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Products.objects.get(qr_code=sale.qr_code)
        except Products.DoesNotExist:
            return Response(
                {"error": f"Produto com QR Code '{sale.qr_code}' não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        product.quantity += refund_quantity
        product.save()

       
        sale.quantity -= refund_quantity 
        sale.total_price = sale.product_price * sale.quantity 
        if sale.quantity == 0:
            sale.refund = True 
        sale.save()

        return Response(
            {"message": "Reembolso realizado com sucesso.",
             "sale_id": sale.id,
             "updated_stock": product.quantity,
             "remaining_quantity_in_sale": sale.quantity},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": f"Erro interno: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
