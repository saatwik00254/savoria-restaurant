import stripe
import json
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from orders.models import Order
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    try:
        line_items = []
        for item in order.order_items.all():
            line_items.append({
                'price_data': {
                    'currency': 'inr',
                    'product_data': {'name': item.item_name},
                    'unit_amount': int(item.unit_price * 100),
                },
                'quantity': item.quantity,
            })
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(f'/payments/success/?order_id={order.pk}'),
            cancel_url=request.build_absolute_uri(f'/payments/cancel/?order_id={order.pk}'),
            metadata={'order_id': order.pk},
        )
        order.stripe_session_id = session.id
        order.save()
        Payment.objects.update_or_create(
            order=order,
            defaults={
                'stripe_session_id': session.id,
                'amount': order.total_amount,
                'currency': 'inr',
                'status': 'pending',
            }
        )
        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('checkout')


@login_required
def payment_success(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    order.payment_status = 'paid'
    order.status = 'confirmed'
    order.save()
    if hasattr(order, 'payment'):
        order.payment.status = 'completed'
        order.payment.save()
    return render(request, 'payments/success.html', {'order': order})


@login_required
def payment_cancel(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'payments/cancel.html', {'order': order})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['metadata'].get('order_id')
        if order_id:
            try:
                order = Order.objects.get(pk=order_id)
                order.payment_status = 'paid'
                order.status = 'confirmed'
                order.save()
            except Order.DoesNotExist:
                pass
    return HttpResponse(status=200)
