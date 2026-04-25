from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from menu.models import MenuItem
from .models import Cart, CartItem, Order, OrderItem


def get_or_create_cart(request):
    """Helper: get or create cart for logged-in user or session."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_view(request):
    cart = get_or_create_cart(request)
    items = cart.cart_items.select_related('menu_item').all()
    return render(request, 'orders/cart.html', {'cart': cart, 'items': items})


def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, pk=item_id, is_available=True)
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.get_item_count()})
    messages.success(request, f'"{item.name}" added to cart.')
    return redirect('cart')


def update_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))
    if quantity <= 0:
        cart_item.delete()
        messages.info(request, 'Item removed from cart.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
    return redirect('cart')


def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    cart_item.delete()
    messages.info(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    items = cart.cart_items.select_related('menu_item').all()
    if not items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('menu')
    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        notes = request.POST.get('notes', '').strip()
        if not address:
            messages.error(request, 'Please enter a delivery address.')
            return render(request, 'orders/checkout.html', {'cart': cart, 'items': items})
        order = Order.objects.create(
            user=request.user,
            delivery_address=address,
            phone=phone,
            notes=notes,
            total_amount=cart.get_total(),
        )
        for ci in items:
            OrderItem.objects.create(
                order=order,
                menu_item=ci.menu_item,
                item_name=ci.menu_item.name,
                quantity=ci.quantity,
                unit_price=ci.menu_item.price,
            )
        # Clear cart
        cart.cart_items.all().delete()
        request.session['pending_order_id'] = order.pk
        return redirect('create_checkout_session', order_id=order.pk)
    return render(request, 'orders/checkout.html', {'cart': cart, 'items': items})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
