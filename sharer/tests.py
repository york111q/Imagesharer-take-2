from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase

from .models import AccountTier, MyUser

from PIL import Image
import io, os

# Create your tests here.

class TestSetUp(APITestCase):

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.images_url = reverse('images')
        self.overview_url = reverse('overview')

        self.users_data = [({'username': 'basicuser', 'password': '1qasw23ed'},
                            {'acc_type': 'Basic'}),
                           ({'username': 'premiumuser', 'password': '1qasw23ed'},
                            {'acc_type': 'Premium'}),
                           ({'username': 'enterpruser', 'password': '1qasw23ed'},
                            {'acc_type': 'Enterprise'})]

        AccountTier.objects.get_or_create(name="Basic")
        AccountTier.objects.get_or_create(name="Premium",
                                          large_thumb_allow=True,
                                          original_img_allow=True)
        AccountTier.objects.get_or_create(name="Enterprise",
                                          large_thumb_allow=True,
                                          original_img_allow=True,
                                          expiring_link_allow=True)

        for user_data in self.users_data:
            user = get_user_model().objects.create_user(username=user_data[0]['username'],
                                                        password=user_data[0]['password'])
            user.account_type = AccountTier.objects.get(name=user_data[1]['acc_type'])
            user.save()

        return super().setUp()

    def tearDown(self):
        return super().tearDown()


class TestUserLogin(TestSetUp):

    def test_user_login_view(self):
        response = self.client.post(self.login_url, self.users_data[0][0],
                                    format="json")
        self.assertEqual(response.status_code, 202)

    def test_user_images_get_view(self):
        self.client.post(self.login_url, self.users_data[0][0], format="json")
        response = self.client.get(self.images_url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_user_images_without_login(self):
        response = self.client.get(self.images_url, format="json")
        self.assertEqual(response.status_code, 401)

    def generate_image_file(self, extension):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(500, 500), color=(100, 100, 100))
        image.save(file, extension)
        file.name = 'test.' + extension
        file.seek(0)
        return file

    def test_image_upload(self):
        image = self.generate_image_file('png')
        data = {'image': image}

        self.client.post(self.login_url, self.users_data[0][0], format="json")
        response = self.client.post(self.images_url, data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_image_upload_wrong_extension(self):
        image = self.generate_image_file('gif')
        data = {'image': image}

        self.client.post(self.login_url, self.users_data[0][0], format="json")
        response = self.client.post(self.images_url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
