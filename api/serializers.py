from rest_framework import serializers, validators
from api.models import ApiUser, Warehouse, Product, Shipment


class ClientSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128, validators=[
     validators.UniqueValidator(ApiUser.objects.all())
    ])
    email = serializers.EmailField(validators=[
     validators.UniqueValidator(ApiUser.objects.all())
    ])
    password = serializers.CharField(min_length=6, max_length=128, write_only=True)
    group = serializers.ChoiceField(choices=ApiUser.ROLE_CHOICES)

    class Meta:
        model = ApiUser
        fields = ['username', 'email', 'password', 'group']
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        client = ApiUser.objects.create(
            email=validated_data["email"],
            username=validated_data["username"],
            group=validated_data['group']
        )

        client.set_password(validated_data["password"])
        client.save(update_fields=["password"])
        return client

    def update(self, instance, validated_data):
        if email := validated_data.get("email"):
            instance.email = email
            instance.save(update_field=["email"])
        if password := validated_data.get("password"):
            instance.set_password(password)
            instance.save(update_field=["password"])
        return instance

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {"id": {"read_only": True}}

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = "__all__"
        extra_kwargs = {"id": {"read_only": True}}

class ShipmentSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.exclude(shipments__isnull=False)
    )

    class Meta:
        model = Shipment
        fields = '__all__'
        extra_kwargs = {"id": {"read_only": True}}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductSerializer(instance.product).data
        return representation