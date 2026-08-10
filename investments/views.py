from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import StockTransaction, ShareInventory
from .serializers import StockTransactionSerializer, ShareInventorySerializer


class StockTransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = StockTransactionSerializer

    def get_queryset(self):
        if not StockTransaction.objects.exists():
            default_txs = [
                StockTransaction(date="2024-04-18", symbol="RIDI", shares=295, buying_price=252.5, buy_amount_with_tax=74488, selling_price=287, sell_amount_after_tax=84373, profit_loss=9885, status="Sold"),
                StockTransaction(date="2024-04-29", symbol="UMHL", shares=215, buying_price=354, buy_amount_with_tax=76373, status="Holding", remarks="Pradeep"),
                StockTransaction(date="2024-04-29", symbol="MHNL", shares=200, buying_price=386.59, buy_amount_with_tax=77320, status="Holding", remarks="Sandesh"),
                StockTransaction(date="2024-08-29", symbol="PRVU", shares=577, buying_price=251.5, buy_amount_with_tax=145116, status="Holding", remarks="Pradeep"),
                StockTransaction(date="2024-09-15", symbol="MHNL", shares=760, buying_price=280.87, buy_amount_with_tax=213461, status="Holding"),
                StockTransaction(date="2024-09-23", symbol="PRVU", shares=80, buying_price=235, buy_amount_with_tax=18800, status="Holding", remarks="Pradeep"),
                StockTransaction(date="2024-10-18", symbol="UMHL", shares=215, selling_price=388, sell_amount_after_tax=83473, profit_loss=7100, status="Sold", remarks="Pradeep"),
                StockTransaction(date="2024-10-16", symbol="MHNL", shares=300, buying_price=271, buy_amount_with_tax=81300, status="Holding", remarks="Pradeep"),
                StockTransaction(date="2024-11-24", symbol="MHNL", shares=400, selling_price=274, sell_amount_after_tax=128040, profit_loss=-3180, status="Sold", remarks="Pradeep"),
                StockTransaction(date="2024-11-24", symbol="PRVU", shares=600, buying_price=224.5, buy_amount_with_tax=134700, status="Holding", remarks="Pradeep"),
                StockTransaction(date="2025-07-13", symbol="SANIMA", shares=400, buying_price=597.3, buy_amount_with_tax=59705, selling_price=685.3, sell_amount_after_tax=67863, profit_loss=8148, status="Sold", remarks="Pawan"),
                StockTransaction(date="2025-07-14", symbol="DELTI", shares=400, buying_price=567.19, buy_amount_with_tax=56804, selling_price=626.05, sell_amount_after_tax=62093, profit_loss=5298, status="Sold", remarks="Pawan"),
                StockTransaction(date="2025-07-16", symbol="SANIMA", shares=400, buying_price=386.64, buy_amount_with_tax=38639, selling_price=377, sell_amount_after_tax=37498, profit_loss=-1141, status="Sold", remarks="Pawan"),
                StockTransaction(date="2025-07-29", symbol="NIMB", shares=200, buying_price=243.9, buy_amount_with_tax=48780, status="Holding", remarks="Pawan"),
                StockTransaction(date="2025-07-29", symbol="PRVU", shares=200, buying_price=246.5, buy_amount_with_tax=49300, selling_price=185.1, status="Loss", remarks="Pawan"),
            ]
            StockTransaction.objects.bulk_create(default_txs)
        return StockTransaction.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]


class StockTransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockTransaction.objects.all()
    serializer_class = StockTransactionSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class ShareInventoryListCreateView(generics.ListCreateAPIView):
    serializer_class = ShareInventorySerializer

    def get_queryset(self):
        if not ShareInventory.objects.exists():
            default_inv = [
                ShareInventory(stock="UMHL", no_of_kitta=215),
                ShareInventory(stock="MHNL", no_of_kitta=580),
                ShareInventory(stock="PRVU", no_of_kitta=1377),
                ShareInventory(stock="NIMB", no_of_kitta=200),
            ]
            ShareInventory.objects.bulk_create(default_inv)
        return ShareInventory.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]


class ShareInventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShareInventory.objects.all()
    serializer_class = ShareInventorySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
