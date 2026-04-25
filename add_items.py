import os
import sys
import django

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from menu.models import Category, MenuItem
from django.utils.text import slugify
from django.utils import timezone

now = timezone.now()

starters  = Category.objects.get(slug='starters')
main      = Category.objects.get(slug='main-course')
desserts  = Category.objects.get(slug='desserts')
beverages = Category.objects.get(slug='beverages')

new_items = [
    # Starters
    dict(category=starters,  name='Caesar Salad',      description='Crisp romaine lettuce, house-made Caesar dressing, golden croutons, and shaved Parmesan.',                              price='229.00', is_vegetarian=True,  is_spicy=False, is_featured=False, image='menu_items/caesar_salad.png'),
    dict(category=starters,  name='Stuffed Mushrooms', description='Portobello caps filled with herbed cream cheese and panko breadcrumbs, baked golden.',                                  price='199.00', is_vegetarian=True,  is_spicy=False, is_featured=False, image='menu_items/stuffed_mushrooms.png'),
    dict(category=starters,  name='Garlic Bread',      description='Thick-cut baguette toasted with house garlic butter, fresh herbs, and melted mozzarella.',                              price='149.00', is_vegetarian=True,  is_spicy=False, is_featured=False, image='menu_items/garlic_bread.png'),
    # Main Course
    dict(category=main,      name='Lamb Rogan Josh',   description='Slow-braised tender lamb in an aromatic Kashmiri sauce of whole spices, yogurt and saffron.',                           price='549.00', is_vegetarian=False, is_spicy=True,  is_featured=True,  image=''),
    dict(category=main,      name='Pasta Carbonara',   description='Silky egg-yolk and Pecorino Romano sauce, crispy pancetta, freshly cracked black pepper.',                              price='429.00', is_vegetarian=False, is_spicy=False, is_featured=False, image=''),
    dict(category=main,      name='Chicken Biryani',   description='Fragrant saffron rice layered with spiced chicken, fried onions and fresh mint. Served with raita.',                   price='349.00', is_vegetarian=False, is_spicy=True,  is_featured=True,  image=''),
    dict(category=main,      name='Margherita Pizza',  description='Thin crispy base with San Marzano tomato sauce, buffalo mozzarella, fresh basil and olive oil.',                       price='379.00', is_vegetarian=True,  is_spicy=False, is_featured=False, image=''),
    dict(category=main,      name='Palak Paneer',      description='Cottage cheese cubes in a velvety spiced spinach gravy, finished with cream and ginger julienne.',                     price='289.00', is_vegetarian=True,  is_spicy=False, is_featured=False, image=''),
    # Desserts
    dict(category=desserts,  name='Tiramisu',          description='Classic Italian dessert - espresso-soaked ladyfingers layered with mascarpone cream and dark cocoa.',                  price='249.00', is_vegetarian=True,  is_spicy=False, is_featured=True,  image=''),
    dict(category=desserts,  name='Mango Cheesecake',  description='No-bake creamy cheesecake with a golden Alphonso mango glaze on a buttery biscuit crumb base.',                        price='229.00', is_vegetarian=True,  is_spicy=False, is_featured=False, image=''),
    dict(category=desserts,  name='Creme Brulee',      description='Silky French vanilla custard with a perfectly caramelized sugar crust, served with seasonal berries.',                 price='269.00', is_vegetarian=True,  is_spicy=False, is_featured=False, image=''),
    # Beverages
    dict(category=beverages, name='Cold Brew Coffee',  description='Slow-steeped 16-hour cold brew served over ice with a choice of black or with cream.',                                 price='149.00', is_vegetarian=True,  is_spicy=False, is_featured=False, image=''),
    dict(category=beverages, name='Virgin Mojito',     description='Sparkling fresh lime and mint mocktail over crushed ice - light, refreshing and invigorating.',                        price='129.00', is_vegetarian=True,  is_spicy=False, is_featured=False, image=''),
    dict(category=beverages, name='Masala Chai',       description='Aromatic Indian spiced milk tea brewed with cardamom, ginger, cinnamon and cloves. Served in a kulhad.',               price='79.00',  is_vegetarian=True,  is_spicy=False, is_featured=False, image=''),
]

created = skipped = 0
for data in new_items:
    slug = slugify(data['name'])
    if MenuItem.objects.filter(slug=slug).exists():
        print(f'  [SKIP] {data["name"]}')
        skipped += 1
        continue
    img = data.pop('image')
    obj = MenuItem.objects.create(slug=slug, is_available=True, created_at=now, **data)
    if img:
        obj.image = img
        obj.save()
    print(f'  [OK]   {obj.name} ({obj.category.name}) Rs.{obj.price}')
    created += 1

print(f'\nDone: {created} created, {skipped} skipped. Total items: {MenuItem.objects.count()}')
