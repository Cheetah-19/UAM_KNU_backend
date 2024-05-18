from rest_framework_simplejwt.tokens import AccessToken


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 쿠키에서 JWT 읽기
        access_token_value = request.COOKIES.get('access')

        if access_token_value:
            # JWT 디코딩 시도
            try:
                AccessToken(access_token_value)

                # HTTP Authorization 헤더에 access token 추가
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token_value}'

            # JWT 디코딩 실패
            except Exception as e:
                pass

        response = self.get_response(request)

        return response
