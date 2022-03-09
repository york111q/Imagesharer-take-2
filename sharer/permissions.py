from rest_framework import permissions
from .models import UserAccountTier

class ExpiryLinksPermission(permissions.BasePermission):
    message = 'Expiry links are available only for higher tier accounts.'

    def has_permission(self, request, view):

         if request.method == "GET":
             return True
         else:
             user_account = UserAccountTier.objects.get(user=request.user)
             return user_account.account_tier.expiry_link


class OriginalImagePermission(permissions.BasePermission):
    message = 'Original image view is available only for higher tier accounts.'

    def has_permission(self, request, view):
         user_account = UserAccountTier.objects.get(user=request.user)
         return user_account.account_tier.original_img_link
