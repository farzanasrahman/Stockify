from django.urls import path
from . import views

urlpatterns = [
    # Fetches and displays stock details.
    path('stock_table/', views.stock_fetch, name='stock-list'),

    # Provides an interface for users to buy stocks.
    path('buy/', views.buy_stock, name='buy-stock'),

    # Provides an interface for users to sell their stocks.
    path('sell/', views.sell_stock, name='sell-stock')
]