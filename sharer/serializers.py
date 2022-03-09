from rest_framework import serializers

from .models import UserImage, ImageThumb


class ImageThumbListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='sharer:thumbnail-detail',
        lookup_field='code')

    class Meta:
        model = ImageThumb
        fields = ['url', 'image_file', 'size', 'code', 'expiry_date']


class OriginalImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UserImage
        fields = ['url', 'code']


class UserImageSerializer(serializers.ModelSerializer):
    thumbnails = ImageThumbListSerializer(many=True, read_only=True)

    class Meta:
        model = UserImage
        fields = ['thumbnails']


class UserImageWithOriginalSerializer(serializers.HyperlinkedModelSerializer):
    thumbnails = ImageThumbListSerializer(many=True, read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='sharer:userimage-detail',
        lookup_field='code')

    class Meta:
        model = UserImage
        fields = ['code', 'url', 'thumbnails']


class ImageThumbSerializer(serializers.ModelSerializer):
    expire_after_seconds = serializers.IntegerField()

    class Meta:
        model = ImageThumb
        fields = ('expire_after_seconds', )

    def validate(self, data):
        expire = int(data['expire_after_seconds'])
        if expire < 300 or expire > 30000:
            raise serializers.ValidationError('Number of seconds should be in'
                                              'range: 300-30000')
        return data
