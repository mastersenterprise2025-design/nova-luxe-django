from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_view, name='search'),
    path('discounts/', views.discounts_view, name='discounts'),
    path('latest/', views.latest_view, name='latest'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('footwear/', views.footwear_view, name='footwear'),
    path('jewellery/', views.jewellery_view, name='jewellery'),
    path('clothes/', views.clothes_view, name='clothes'),
    path('category/<int:category_id>/', views.category_view, name='category'),
]
