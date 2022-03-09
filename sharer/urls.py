from django.urls import path, include

from rest_framework.authtoken.views import obtain_auth_token

from . import views

app_name = 'sharer'

urlpatterns = [
    path('', views.api_root),
    path('images/', views.UserImageView.as_view(), name='images'),
    path('image/<str:code>', views.DetailImageView.as_view(), name='userimage-detail'),
    path('thumbnail/<str:code>', views.DetailThumbnailView.as_view(), name='thumbnail-detail')
]
