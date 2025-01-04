# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from .models import Products, StockHistory
import random
import string
from datetime import datetime
from rest_framework.decorators import api_view
from sgeStore.decorators import role_required
from rest_framework.response import Response
from rest_framework import status
from userAcessJWT.models import CustomUser
def _generate_unique_id(name, price, gender):
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
        user_id = request.data.get('user_id')

        if not all([name, price, gender, quantity]):
            raise ValueError("Missing required fields")

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            return JsonResponse({"error": "Price and quantity must be valid numbers."}, status=400)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)
        
        unique_id = _generate_unique_id(name, price, gender)

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

        update_product_in_stock(
            product=product,
            action='Adicionado',
            field_changed='Estoque',
            old_value='',
            new_value='',
            old_quantity=0,
            new_quantity=quantity, 
            user=user
        )

        return JsonResponse({"message": "Product created successfully", "product_id": unique_id})

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    

@role_required('mod')
@api_view(['PUT'])
def update_product(request):
    product_id = request.data.get('product_id')
    user_id = request.data.get('user_id')

    if not product_id:
        return Response({"error": "Product ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Products.objects.get(qr_code=product_id)
        user = CustomUser.objects.get(id=user_id)

        name = request.data.get('name', product.name)
        description = request.data.get('description', product.description)
        gender = request.data.get('gender', product.gender)
        quantity = request.data.get('quantity', product.quantity)

        updated_fields = []
        field_changes = {}

        if name != product.name:
            field_changes['name'] = (product.name, name)
            product.name = name
            updated_fields.append('name')
        if description != product.description:
            field_changes['description'] = (product.description, description)
            product.description = description
            updated_fields.append('description')
        if gender != product.gender:
            field_changes['gender'] = (product.gender, gender)
            product.gender = gender
            updated_fields.append('gender')
        if quantity != product.quantity:
            field_changes['quantity'] = (product.quantity, quantity)
            product.quantity = quantity
            updated_fields.append('quantity')

        product.save()

        for field in updated_fields:
            old_value, new_value = field_changes[field]
            update_product_in_stock(
                product=product,
                action='Atualizado',
                field_changed=field,
                old_value=str(old_value),
                new_value=str(new_value),
                old_quantity=product.quantity,
                new_quantity=quantity,
                user=user
            )

        return Response({"message": "Product updated successfully."}, status=status.HTTP_200_OK)

    except Products.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@role_required('user')
@api_view(['GET'])
def list_product(request):

    try:
        name = request.data.get('name', None)
        gender = request.data.get('gender', None)
        price_min = request.data.get('price_min', None)
        price_max = request.data.get('price_max', None)
        date_min = request.data.get('date_min', None)
        date_max = request.data.get('date_max', None)
        limit = request.data.get('limit', None)

        products = Products.objects.all()

        if name:
            products = products.filter(name__icontains=name)
        if gender:
            products = products.filter(gender=gender)
        if price_min:
            products = products.filter(price__gte=float(price_min))
        if price_max:
            products = products.filter(price__lte=float(price_max))
        if date_min:
            products = products.filter(qr_code_creation_date__gte=date_min)
        if date_max:
            products = products.filter(qr_code_creation_date__lte=date_max)

        if limit:
            products = products[:int(limit)]

        product_data = [
            {
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "gender": product.gender,
                "quantity": product.quantity,
                "qr_code": product.qr_code,
                "qr_code_generated": product.qr_code_generated,
                "qr_code_creation_date": product.qr_code_creation_date
            }
            for product in products
        ]

        return Response({"products": product_data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@role_required('mod')
@api_view(['DELETE'])
def delete_product(request):
    product_id = request.data.get('product_id')
    user_id = request.data.get('user_id')

    if not product_id:
        return Response({"error": "Product ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Products.objects.get(qr_code=product_id)

        user = CustomUser.objects.get(id=user_id)

        update_product_in_stock(
            product=product,
            action='Deletado',
            field_changed='Estoque',
            old_value='',
            new_value='',
            old_quantity=product.quantity,
            new_quantity=0,
            user=user
        )

        product.delete()

        return Response({"message": "Product deleted successfully."}, status=status.HTTP_200_OK)

    except Products.DoesNotExist:
        return Response({"error": "No product exists with this ID."}, status=status.HTTP_400_BAD_REQUEST)

def update_product_in_stock(product, action, field_changed, old_value, new_value, old_quantity, new_quantity, user):
  
    history = StockHistory.objects.create(
        product=product.qr_code,
        action=action,
        field_changed=field_changed,
        old_value=old_value,
        new_value=new_value,
        old_quantity=old_quantity,
        new_quantity=new_quantity,
        user=user.username
    )

    history.save()
