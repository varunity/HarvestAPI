import django_filters
from farmers.models import Farmer, Receipt, Farm, Crop, Livestock, Price
from farmers.serializers import FarmerSerializer, ReceiptSerializer, FarmSerializer, CropSerializer, LivestockSerializer, PriceSerializer
 
from rest_framework import generics
from rest_framework import permissions
from django.contrib.auth.models import User
from farmers.serializers import UserSerializer
from farmers.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.decorators import link

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from django.contrib.auth import get_user_model
from rest_framework import status, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token


class FarmerViewSet(viewsets.ModelViewSet):
    """
    This view set automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` Farmers.

    """
    authentication_classes = (BasicAuthentication, SessionAuthentication, TokenAuthentication)
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    permission_classes = (IsAuthenticated,)#(permissions.IsAuthenticatedOrReadOnly,
                         # IsOwnerOrReadOnly,)
    filter_fields = ('farmer_idx','farmer_id','first_name','last_name','alias','res_address', 'res_parish','tel_number','cell_number','verified_status','dob','agri_activity')
    filter_backends = (filters.SearchFilter,filters.OrderingFilter,filters.DjangoFilterBackend,)
    search_fields = ('first_name', 'last_name', 'alias', 'res_parish', 'agri_activity')
    ordering_fields = ('first_name', 'last_name', 'alias', 'res_parish', 'agri_activity', 'verified_status', 'dob')

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This view set automatically provides `list` and `detail`  on Users .
    """
    queryset = User.objects.all()
    authentication_classes = (SessionAuthentication,TokenAuthentication)
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'email')

class ReceiptFilter(django_filters.FilterSet):

    parish = django_filters.CharFilter(name="farmer__res_parish")
    farmer_id = django_filters.CharFilter(name="farmer__farmer_id")

    class Meta:
        model = Receipt
        fields = ['farmer','receipt_no', 'rec_range1', 'rec_range2', 'investigation_status', 'remarks','farmer_id','parish']


class ReceiptViewSet(viewsets.ModelViewSet):
    """
    This view set automatically provides `list` and `detail` on Receipts.
    """
    queryset = Receipt.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = ReceiptSerializer
    filter_class = ReceiptFilter
    filter_backends = (filters.SearchFilter,filters.OrderingFilter,filters.DjangoFilterBackend,)
    search_fields = ('remarks')
    ordering_fields = ('farmer', 'investigation_status')

class FarmFilter(django_filters.FilterSet):

    farmer_id = django_filters.CharFilter(name="farmer__farmer_id")
    min_size = django_filters.NumberFilter(name="farm_size", lookup_type='gte')
    max_size = django_filters.NumberFilter(name="farm_size", lookup_type='lte')
    class Meta:
        model = Farm
        fields = ['farmer_idx','farmer_id','farm_address','farm_id','parish','district','extension','farm_size','lat','long','farm_status','farmer','min_size','max_size']



class FarmViewSet(viewsets.ModelViewSet):
    """
    This view show Farmer's Farm
    """
    queryset = Farm.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = FarmSerializer
    filter_class = FarmFilter
    filter_backends = (filters.SearchFilter,filters.OrderingFilter,filters.DjangoFilterBackend,)
    search_fields = ('parish','farm_address','farm_id','farmer_idx', 'extension', 'farm_status', 'farm_size')
    ordering_fields = ('parish','district')


class CropFilter(django_filters.FilterSet):

    parish = django_filters.CharFilter(name="farm__parish")
    farm_id = django_filters.CharFilter(name="farm__farm_id")
    min_vol = django_filters.NumberFilter(name="estimated_vol", lookup_type='gte')
    max_vol = django_filters.NumberFilter(name="estimated_vol", lookup_type='lte')

    class Meta:
        model = Crop
        fields = ['crop_name', 'common_name', 'farm','farm__farm_id', 'parish', 'min_vol', 'max_vol']

class CropViewSet(viewsets.ModelViewSet):
    """
    This view shows Crops on a Farm
    """

    queryset = Crop.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = CropSerializer
    filter_class = CropFilter
    filter_backends = (filters.SearchFilter,filters.OrderingFilter,filters.DjangoFilterBackend,)
    search_fields = ('crop_name',)
    ordering_fields = ('crop_name', 'farm', 'farm_id')


class LivestockFilter(django_filters.FilterSet):

    parish = django_filters.CharFilter(name="farm__parish")
    farm_id = django_filters.CharFilter(name="farm__farm_id")

    class Meta:
        model = Livestock
        fields = ['livestock_name', 'farm','farm_id', 'parish']

class LivestockViewSet(viewsets.ModelViewSet):
    """
    This view shows Livestock on a Farm
    """

    queryset = Livestock.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = LivestockSerializer
    filter_class = LivestockFilter
    filter_backends = (filters.SearchFilter,filters.OrderingFilter,filters.DjangoFilterBackend,)
    search_fields = ('livestock_name',)
    ordering_fields = ('livestock_name', 'farm', 'farm_id')


class PriceFilter(django_filters.FilterSet):

    min_price = django_filters.NumberFilter(name="price", lookup_type='gte')
    max_price = django_filters.NumberFilter(name="price", lookup_type='lte')

    class Meta:
        model = Price
        fields = ['price_id','price','public','price_point','parish','commodity','crop_code','units','variety','batch_date','published_on','extension','min_price','max_price',]

class PriceViewSet(viewsets.ModelViewSet):
    """
    This view shows Crop Prices
    """

    queryset = Price.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = PriceSerializer
    filter_class = PriceFilter
    filter_backends = (filters.SearchFilter,filters.OrderingFilter,filters.DjangoFilterBackend,)
    search_fields = ('commodity', 'crop_code', 'price_point', 'extension', 'parish')
    ordering_fields = ('commodity', 'crop_code', 'price_point', 'extension', 'parish')


@api_view(['POST'])
def register(request):
    VALID_USER_FIELDS = [f.name for f in get_user_model()._meta.fields]
    DEFAULTS = {
        # you can define any defaults that you would like for the user, here
    }
    serialized = UserSerializer(data=request.DATA)
    if serialized.is_valid():
        user_data = {field: data for (field, data) in request.DATA.items() if field in VALID_USER_FIELDS}
        user_data.update(DEFAULTS)
        user = get_user_model().objects.create_user(
            **user_data
        )
        return Response(UserSerializer(instance=user).data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)



