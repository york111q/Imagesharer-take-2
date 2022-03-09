from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.utils import timezone

from rest_framework import generics, mixins, status
from rest_framework.decorators import api_view
from rest_framework.authentication import (TokenAuthentication,
                                           SessionAuthentication)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .models import UserImage, codemaker, ImageThumb, UserAccountTier
from .permissions import ExpiryLinksPermission, OriginalImagePermission
from .serializers import (UserImageSerializer, ImageThumbSerializer, ImageThumbListSerializer, UserImageWithOriginalSerializer, OriginalImageSerializer) #LoginSerializer,
                          #ImageURLSerializer)

from datetime import timedelta, datetime


# Create your views here.

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'images': reverse('sharer:images', request=request, format=format),
    })


class UserImageView(generics.GenericAPIView, mixins.CreateModelMixin):
    authentication_classes = [SessionAuthentication] #TokenAuthentication,
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        user_account = UserAccountTier.objects.get(user=self.request.user)
        if user_account.account_tier.original_img_link:
            return UserImageWithOriginalSerializer
        else:
            return UserImageSerializer

    def get_queryset(self):
        return UserImage.objects.filter(user=self.request.user)

    def get(self, request):
        images = self.get_queryset()

        for image in images:
            image.prepare_allowed_thumbs()

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(self.get_queryset(), many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        return self.create(request)

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()


class DetailImageView(generics.GenericAPIView):
    serializer_class = OriginalImageSerializer
    queryset = UserImage.objects.all()
    permission_classes = [OriginalImagePermission]

    def get_object(self, code):
        try:
            return UserImage.objects.get(code=code)
        except UserImage.DoesNotExist:
            return False

    def get(self, request, code):
        image = self.get_object(code)

        if image:
            return Response(image.image.url)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class DetailThumbnailView(generics.GenericAPIView):
    serializer_class = ImageThumbSerializer
    queryset = ImageThumb.objects.all()
    permission_classes = [ExpiryLinksPermission]

    def get_object(self, code):
        try:
            return self.queryset.get(code=code)
        except ImageThumb.DoesNotExist:
            return False

    def get(self, request, code):
        thumb = self.get_object(code)

        if thumb:
            if thumb.expiry_date:
                if thumb.expiry_date.replace(tzinfo=None) < datetime.now():
                    thumb.delete()
                    return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(thumb.image_file.url)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, code):
        serializer = ImageThumbSerializer(data=request.data)
        serializer.validate(request.data)

        expiry_sec = int(request.data['expire_after_seconds'])
        expiry_date = datetime.now() + timedelta(seconds=expiry_sec)

        img_obj = ImageThumb.objects.get(code=code)
        img = ImageThumb.objects.create(image_file=img_obj.image_file,
                                        image_object=img_obj.image_object,
                                        size=img_obj.size,
                                        code=codemaker(),
                                        expiry_date=expiry_date)

        user_info = {
                     'Created url': '/thumbnails/' + img.code,
                     'Expire': img.expiry_date.strftime("%m/%d/%Y, %H:%M:%S")
        }

        return Response(user_info, status=status.HTTP_202_ACCEPTED)
