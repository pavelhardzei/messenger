from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from users.models import UserProfile


class SocialAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return

        try:
            user = UserProfile.objects.get(email=sociallogin.user.email)
            sociallogin.connect(request, user)
        except UserProfile.DoesNotExist:
            pass

    def populate_user(self, request, sociallogin, data):
        user = sociallogin.user
        user.email = data.get('email')
        user.user_name = data.get('email').lower().split('@')[0]
        user.full_name = f"{data.get('first_name')} {data.get('last_name')}"
        user.is_active = True

        return user
