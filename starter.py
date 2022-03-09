import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imgsharer.settings')
import django
django.setup()

from sharer.models import AccountTier, Thumbnail

thumb200, c = Thumbnail.objects.get_or_create(size=200)
thumb400, c = Thumbnail.objects.get_or_create(size=400)

tier_basic, c = AccountTier.objects.get_or_create(name="Basic")
tier_premium, c = AccountTier.objects.get_or_create(name="Premium",
                                                    original_img_link=True)
tier_enterprise, c = AccountTier.objects.get_or_create(name="Enterprise",
                                                       original_img_link=True,
                                                       expiry_link=True)

tier_basic.thumbnails.add(thumb200)
tier_premium.thumbnails.add(thumb200, thumb400)
tier_enterprise.thumbnails.add(thumb200, thumb400)
