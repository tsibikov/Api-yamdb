from rest_framework_simplejwt.tokens import RefreshToken


class Token():
    def __init__(self, access, refresh):
        self.access = access
        self.refresh = refresh


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    token = Token(
        access=str(refresh.access_token),
        refresh=str(refresh)
    )
    data = (token, True)
    return data
