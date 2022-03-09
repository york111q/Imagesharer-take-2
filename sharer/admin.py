from django.contrib import admin

from .models import (AccountTier, UserImage, ImageThumb, Thumbnail,
                     UserAccountTier)


# Register your models here.
class ImageThumbAdmin(admin.ModelAdmin):
    list_display = ['image_object', 'size', 'code', 'expiry_date']
    list_filter = ['image_object', 'expiry_date']
    ordering = ['image_object', 'size', 'expiry_date']


class ImageThumbInline(admin.TabularInline):
    model = ImageThumb
    readonly_fields = ['image_object', 'image_file', 'size', 'code',
                       'expiry_date']
    max_num = 0


class UserImageAdmin(admin.ModelAdmin):
    list_display = ['user', 'image', 'code']
    list_filter = ['user']
    ordering = ['user']
    inlines = [ImageThumbInline]


admin.site.register(AccountTier)
admin.site.register(UserImage, UserImageAdmin)
admin.site.register(ImageThumb, ImageThumbAdmin)
admin.site.register(Thumbnail)
admin.site.register(UserAccountTier)
