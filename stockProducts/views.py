# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from .models import Products
import random
import string
from datetime import datetime
from rest_framework.decorators import api_view
from sgeStore.decorators import role_required
from rest_framework.response import Response
from rest_framework import status

def generate_unique_id(name, price, gender):
    name_initial = name[0].upper()
    price_digits = str(int(price))[:2]
    gender_code = gender
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    unique_id = f"{name_initial}{price_digits}{gender_code}{random_part}"
    return unique_id

@role_required('mod')
@api_view(['POST'])
def create_product(request):
    try:
        name = request.data.get('name')
        price = request.data.get('price')
        gender = request.data.get('gender')
        quantity = request.data.get('quantity')
        description = request.data.get('description', '')

        if not all([name, price, gender, quantity]):
            raise ValueError("Missing required fields")

        unique_id = generate_unique_id(name, price, gender)

        product = Products(
            name=name,
            description=description,
            price=price,
            gender=gender,
            quantity=quantity,
            qr_code=unique_id,
            qr_code_generated=True,
            qr_code_creation_date=datetime.now().date()
        )

        product.save()
        
        return JsonResponse({"message": "Product created successfully", "product_id": unique_id})

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
@role_required('admin')


@api_view(['DELETE'])
def delete_product(request):

    product_id = request.data.get('product_id')

    if not product_id:
        return Response({"error": "Product ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Products.objects.get(qr_code=product_id)

        product.delete()

        return Response({"message": "Product deleted successfully."}, status=status.HTTP_200_OK)

    except Products.DoesNotExist:
        return Response({"error": "No product exists with this ID."}, status=status.HTTP_400_BAD_REQUEST)
    