from django.urls import path
from .views import (
    StockTransactionListCreateView,
    StockTransactionDetailView,
    ShareInventoryListCreateView,
    ShareInventoryDetailView,
)

urlpatterns = [
    path("stocks/", StockTransactionListCreateView.as_view(), name="stock-list-create"),
    path("stocks/<int:pk>/", StockTransactionDetailView.as_view(), name="stock-detail"),
    path("inventory/", ShareInventoryListCreateView.as_view(), name="inventory-list-create"),
    path("inventory/<int:pk>/", ShareInventoryDetailView.as_view(), name="inventory-detail"),
]
