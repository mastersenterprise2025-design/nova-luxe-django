from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from decimal import Decimal
from .models import Product, Category

def home(request):
    # Get latest products (up to 6)
    latest_products = Product.objects.filter(is_latest=True)[:6]
    
    return render(request, 'store/home.html', {
        'latest_products': latest_products
    })

def category_view(request, category_id):
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, "category.html", {
        "category": category,
        "products": products
    })

def search_view(request):
    # Read query param q from request.GET
    query = request.GET.get('q', '')
    
    # Filter Product where name__icontains=q
    results = Product.objects.filter(name__icontains=query) if query else []
    
    # Return results to template search.html
    # Pass query and results in context
    return render(request, 'store/search.html', {
        'query': query,
        'results': results
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get cart from session or create new
    cart = request.session.get('cart', {})
    
    # Add or update product in cart
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1
    
    # Save cart back to session
    request.session['cart'] = cart
    
    # Add success message
    messages.success(request, f'{product.name} added to cart!')
    
    # Redirect back or to cart
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_count': sum(cart.values())
        })
    
    return redirect('store:cart')

def cart_view(request):
    # Get cart from session
    cart = request.session.get('cart', {})
    
    # Get products from cart
    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total_price += subtotal
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            # Remove invalid product from cart
            del cart[product_id]
    
    # Update cart in session if any invalid products were removed
    request.session['cart'] = cart
    
    # Calculate tax and total
    tax = total_price * Decimal('0.10')  # 10% tax
    grand_total = total_price + tax
    
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'tax': tax,
        'grand_total': grand_total,
        'cart_count': sum(cart.values())
    })

def remove_from_cart(request, product_id):
    # Get cart from session
    cart = request.session.get('cart', {})
    
    # Remove product from cart
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, 'Item removed from cart!')
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart!',
            'cart_count': sum(cart.values())
        })
    
    return redirect('store:cart')

def discounts_view(request):
    # Fetch Product where is_discounted=True
    discounted_products = Product.objects.filter(is_discounted=True)
    
    # Send to discounts.html
    return render(request, 'store/discounts.html', {
        'discounted_products': discounted_products
    })

def latest_view(request):
    # Fetch Product where is_latest=True
    # Order by newest first (assuming you have a created_at field, otherwise order by id descending)
    latest_products = Product.objects.filter(is_latest=True).order_by('-id')
    
    # Send to latest.html
    return render(request, 'store/latest.html', {
        'latest_products': latest_products
    })

def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        action = request.POST.get('action')  # 'increase' or 'decrease'
        
        # Get cart from session
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            current_quantity = cart[product_id_str]
            
            if action == 'increase':
                cart[product_id_str] = current_quantity + 1
                message = 'Quantity increased!'
            elif action == 'decrease' and current_quantity > 1:
                cart[product_id_str] = current_quantity - 1
                message = 'Quantity decreased!'
            else:
                return JsonResponse({'success': False, 'message': 'Invalid action or quantity'})
            
            # Save updated cart
            request.session['cart'] = cart
            
            # Calculate new totals
            try:
                product = Product.objects.get(id=product_id)
                new_quantity = cart[product_id_str]
                new_subtotal = product.price * new_quantity
                
                # Recalculate total cart
                total_price = 0
                for pid, qty in cart.items():
                    try:
                        p = Product.objects.get(id=pid)
                        total_price += p.price * qty
                    except Product.DoesNotExist:
                        continue
                
                tax = total_price * Decimal('0.10')
                grand_total = total_price + tax
                
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'new_quantity': new_quantity,
                    'new_subtotal': float(new_subtotal),
                    'total_price': float(total_price),
                    'tax': float(tax),
                    'grand_total': float(grand_total),
                    'cart_count': sum(cart.values())
                })
            except Product.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Product not found'})
        
        return JsonResponse({'success': False, 'message': 'Product not in cart'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def footwear_view(request):
    # Find the root category
    try:
        footwear_category = Category.objects.get(name='Footwear')
    except Category.DoesNotExist:
        return render(request, 'store/section.html', {
            'category_name': 'Footwear',
            'products': [],
            'error': 'Footwear category not found'
        })
    
    # Fetch all child categories recursively
    all_categories = [footwear_category]
    
    def get_all_children(parent_category):
        children = Category.objects.filter(parent=parent_category)
        for child in children:
            all_categories.append(child)
            get_all_children(child)  # Recursive call for nested categories
    
    get_all_children(footwear_category)
    
    # Fetch all products under these categories
    products = Product.objects.filter(category__in=all_categories)
    
    return render(request, 'store/section.html', {
        'category_name': 'Footwear Collection',
        'products': products
    })

def jewellery_view(request):
    # Find the root category
    try:
        jewellery_category = Category.objects.get(name='Jewellery')
    except Category.DoesNotExist:
        return render(request, 'store/section.html', {
            'category_name': 'Jewellery',
            'products': [],
            'error': 'Jewellery category not found'
        })
    
    # Fetch all child categories recursively
    all_categories = [jewellery_category]
    
    def get_all_children(parent_category):
        children = Category.objects.filter(parent=parent_category)
        for child in children:
            all_categories.append(child)
            get_all_children(child)  # Recursive call for nested categories
    
    get_all_children(jewellery_category)
    
    # Fetch all products under these categories
    products = Product.objects.filter(category__in=all_categories)
    
    return render(request, 'store/section.html', {
        'category_name': 'Jewellery Collection',
        'products': products
    })

def clothes_view(request):
    # Find the root category
    try:
        clothes_category = Category.objects.get(name='Clothes')
    except Category.DoesNotExist:
        return render(request, 'store/section.html', {
            'category_name': 'Clothes',
            'products': [],
            'error': 'Clothes category not found'
        })
    
    # Fetch all child categories recursively
    all_categories = [clothes_category]
    
    def get_all_children(parent_category):
        children = Category.objects.filter(parent=parent_category)
        for child in children:
            all_categories.append(child)
            get_all_children(child)  # Recursive call for nested categories
    
    get_all_children(clothes_category)
    
    # Fetch all products under these categories
    products = Product.objects.filter(category__in=all_categories)
    
    return render(request, 'store/section.html', {
        'category_name': 'Clothes Collection',
        'products': products
    })
