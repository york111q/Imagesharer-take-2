from django.conf import settings
from django.contrib.auth.models import (AbstractUser, AbstractBaseUser,
                                        BaseUserManager, User)
from django.core.files import File
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

import os, random, string
from io import BytesIO
from PIL import Image
from datetime import datetime


THUMB_DIR = os.path.join('sharer', 'thumbnails')


def get_upload_path(userimage, filename):
    return os.path.join('sharer', str(userimage.user.username), str(filename))


def codemaker():
    length = 10
    while True:
        code = ''.join(random.choices(string.ascii_lowercase, k=length))
        if not (UserImage.objects.filter(code=code).exists() or
                ImageThumb.objects.filter(code=code).exists()):
            return code
        else:
            continue

# Create your models here.
class Thumbnail(models.Model):
    size = models.PositiveIntegerField()

    def __str__(self):
        return f'Thumbnail size: {self.size}px'


class AccountTier(models.Model):
    name = models.CharField(max_length=32)
    thumbnails = models.ManyToManyField(Thumbnail, blank=True)
    original_img_link = models.BooleanField(default=False)
    expiry_link = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserAccountTier(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True)
    account_tier = models.ForeignKey(AccountTier,
                                     related_name='users_this_tier',
                                     on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} | {self.account_tier}'


class ImageThumb(models.Model):
    image_object = models.ForeignKey('UserImage',
                                     related_name='thumbnails',
                                     on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to=THUMB_DIR)
    size = models.PositiveIntegerField()
    code = models.CharField(max_length=16, unique=True, null=True)
    expiry_date = models.DateTimeField(null=True)

    def expiry_date_format(self):
        if self.expiry_date:
            return self.expiry_date.strftime('%Y-%m-%d %H:%M')
        else:
            return 'No date'

    def __str__(self):
        return f'{self.size} | {self.image_object.image.name}'


class UserImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_upload_path,
                              validators=[FileExtensionValidator(['jpg',
                                                                  'png'])])
    code = models.CharField(max_length=16, unique=True, default=codemaker)

    def create_thumbnail(self, size):
        im = Image.open(self.image)
        im.convert('RGBA')
        im.thumbnail((size, size))
        thumb_io = BytesIO()
        im.save(thumb_io, 'PNG', quality=85)
        thumbnail = File(thumb_io, name=self.image.name)
        img = ImageThumb.objects.create(image_object=self,
                                        size=size,
                                        image_file=thumbnail,
                                        code=codemaker())
        return img

    def prepare_allowed_thumbs(self):

        account_tier = self.user.useraccounttier.account_tier

        user_allowed_thumbnails = Thumbnail.objects.filter(accounttier=
                                                           account_tier)
        user_allowed_thumbnail_sizes = ([thumbnail.size for thumbnail in
                                         user_allowed_thumbnails])
        user_thumbnails = ImageThumb.objects.filter(image_object=self)

        for thumb_size in user_allowed_thumbnail_sizes:
            if not user_thumbnails.filter(size=thumb_size).exists():
                self.create_thumbnail(thumb_size)

        for thumb in user_thumbnails:
            if not thumb.size in user_allowed_thumbnail_sizes:
                thumb.delete()
            if (thumb.expiry_date and thumb.expiry_date.replace(tzinfo=None) <
                                      datetime.now()):
                thumb.delete()

        return True

    def __str__(self):
        return self.image.name
