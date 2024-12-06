from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from api.models import ApiUser, Warehouse, Product, Shipment
from api.serializers import ClientSerializer, WarehouseSerializer, ProductSerializer, ShipmentSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Выход пользователя из системы.

    Метод: POST

    Разрешения: Только аутентифицированные пользователи.
    """
    logout(request)
    return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class IsSeller(BasePermission):
    """
    Разрешение для продавцов.

    Проверяет, является ли пользователь аутентифицированным и принадлежит ли он к группе "seller".
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.group == 'seller'


class IsBuyer(BasePermission):
    """
    Разрешение для покупателей.

    Проверяет, является ли пользователь аутентифицированным и принадлежит ли он к группе "buyer".
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.group == 'buyer'


class ClientModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления клиентами (ApiUser).

    Методы: POST, GET

    Разрешения: Открыты для всех.

    Поля: queryset, http_method_names, serializer_class, authentication_classes, permission_classes
    """
    queryset = ApiUser.objects.all()
    http_method_names = ['post', 'get']
    serializer_class = ClientSerializer

    authentication_classes = []
    permission_classes = []


class WarehouseModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet для создания склада (Warehouse).

    Методы: CREATE, UPDATE, PARTIAL_UPDATE, DESTROY

    Разрешения: Открыты для всех.

    Поля: queryset, serializer_class.
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSeller()]
        return [IsAuthenticated()]

    @action(detail=True)
    def products(self, request, pk=None):
        warehouse = get_object_or_404(Warehouse.objects.all(), id=pk)
        free_products = warehouse.products.filter(shipments__isnull=True)
        return Response(
            ProductSerializer(free_products, many=True).data
        )


class ProductModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet для создания продукта(Product).

    Методы: CREATE, UPDATE, PARTIAL_UPDATE, DESTROY

    Разрешения: Открыты для всех.

    Поля: queryset, serializer_class.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        if self.action == 'list':
            queryset = queryset.exclude(shipments__isnull=False)
        return queryset

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSeller()]
        return [IsAuthenticated()]


class ShipmentModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet для создания отгрузки(Shipment).

    Методы: CREATE

    Разрешения: Открыты для всех.

    Поля: queryset, serializer_class, filter_backends.
    """
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self):
        if self.action in ['list', 'create']:
            return [IsBuyer()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
