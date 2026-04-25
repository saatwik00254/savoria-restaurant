from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from menu.models import Category, MenuItem
from orders.models import Order
from accounts.models import UserProfile


def is_admin_or_staff(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    try:
        return user.profile.role in ('admin', 'staff')
    except Exception:
        return False


admin_required = user_passes_test(is_admin_or_staff, login_url='/accounts/login/')


@login_required
@admin_required
def dashboard_index(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_revenue = Order.objects.filter(payment_status='paid').aggregate(
        total=Sum('total_amount'))['total'] or 0
    total_users = User.objects.filter(is_staff=False).count()

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    # Revenue for last 7 days (for chart)
    revenue_data = []
    labels = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        rev = Order.objects.filter(
            created_at__date=day, payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        revenue_data.append(float(rev))
        labels.append(day.strftime('%a'))

    # Popular items
    from orders.models import OrderItem
    popular_items = OrderItem.objects.values('item_name').annotate(
        total_qty=Sum('quantity')
    ).order_by('-total_qty')[:5]

    return render(request, 'dashboard/index.html', {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'revenue_labels': labels,
        'revenue_data': revenue_data,
        'popular_items': popular_items,
    })


@login_required
@admin_required
def dashboard_orders(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('user').order_by('-created_at')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'dashboard/orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': Order._meta.get_field('status').choices,
    })


@login_required
@admin_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = [s[0] for s in Order._meta.get_field('status').choices]
        if new_status in valid:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.pk} status updated to {new_status}.')
    return redirect('dashboard_orders')


@login_required
@admin_required
def dashboard_menu(request):
    categories = Category.objects.all()
    items = MenuItem.objects.select_related('category').order_by('category', 'name')
    return render(request, 'dashboard/menu_management.html', {
        'categories': categories, 'items': items
    })


@login_required
@admin_required
def toggle_item_availability(request, item_id):
    item = get_object_or_404(MenuItem, pk=item_id)
    item.is_available = not item.is_available
    item.save()
    messages.success(request, f'"{item.name}" availability updated.')
    return redirect('dashboard_menu')


@login_required
@admin_required
def dashboard_users(request):
    users = User.objects.select_related('profile').order_by('-date_joined')
    return render(request, 'dashboard/users.html', {'users': users})


@login_required
@admin_required
def toggle_user_active(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        messages.success(request, f'User "{user.username}" active status updated.')
    return redirect('dashboard_users')
