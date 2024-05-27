from rest_framework.views import APIView
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from ..optimizations.models import *
from ..optimizations.serializers import *
from rest_framework_simplejwt.views import TokenRefreshView


class RegisterView(APIView):
    def post(self, request):
        # 역직렬화 (JSON -> model)
        serializer = UserSerializer(data=request.data)

        # 유효성 검사
        if serializer.is_valid():
            # DB에 저장
            user = serializer.save()
            return Response({'result': 'success', 'data': {'id': user.id, 'phone_number': user.phone_number}}, status=status.HTTP_200_OK)

        return Response({'result': 'fail', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AuthView(APIView):
    # 로그인
    def post(self, request):
        # user 탐색
        user = authenticate(id=request.data.get("id"), password=request.data.get("password"))

        if user is not None:
            # JWT 발급
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    'result': 'success',
                    'data': {
                        'id': user.id,
                        'token': {
                            "access": access_token,
                            "refresh": refresh_token,
                        },
                        'admin': user.is_admin
                    }
                },
                status=status.HTTP_200_OK,
            )

            # JWT을 쿠키에 저장
            res.set_cookie('access', access_token, httponly=True, secure=True, samesite='None')
            res.set_cookie('refresh', refresh_token, httponly=True, secure=True, samesite='None')
            return res
        else:
            return Response({'result': 'fail', 'message': 'The ID or password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

    # 로그아웃
    def delete(self, request):
        # 쿠키에 저장된 JWT 삭제
        response = Response({'result': 'success', 'data': {'id': request.user.id}}, status=status.HTTP_202_ACCEPTED)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response


class ChangeView(APIView):
    # 인증된 사용자만 view 접근 허용
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        password = request.data['new_password1']

        # 이전 비밀번호가 맞지 않음
        if not user.check_password(request.data['old_password']):
            return Response({'result': 'fail', 'message': 'Your old password was entered incorrectly'}, status=status.HTTP_400_BAD_REQUEST)

        # 새 비밀번호 확인이 맞지 않음
        if password != request.data['new_password2']:
            return Response({'result': 'fail', 'message': 'The two password fields didn’t match.'}, status=status.HTTP_400_BAD_REQUEST)

        # 비밀번호 변경
        user.set_password(password)
        user.save()

        # JWT 재발급
        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)
        res = Response(
            {
                'result': 'success',
                'data': {
                    'id': user.id,
                    'token': {
                        "access": access_token,
                        "refresh": refresh_token,
                    }
                }
            },
            status=status.HTTP_200_OK,
        )

        # 재발급한 JWT을 쿠키에 저장
        res.set_cookie('access', access_token, httponly=True, secure=True, samesite='None')
        res.set_cookie('refresh', refresh_token, httponly=True, secure=True, samesite='None')
        return res


class HistoryView(APIView):
    # 인증된 사용자만 view 접근 허용
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # params
        vertiport_name = request.GET.get('vertiport', None)
        state_sequence = request.GET.get('sequence', None)

        if vertiport_name:
            vertiport = Vertiport.objects.filter(name=vertiport_name).first()
            states = State.objects.filter(user=request.user, vertiport=vertiport)

            # 버티포트만 선택됨
            if not state_sequence:
                return Response({'result': 'success', 'data': {'states': StateSerializer(states, many=True).data}}, status=status.HTTP_200_OK)

            # 버티포트랑 식별번호 선택됨
            else:
                state = states.filter(sequence=state_sequence).first()
                optimizations = Optimization.objects.filter(state=state)
                return Response({'result': 'success', 'data': {'optimization': OptimizationSerializer(optimizations, many=True).data}}, status=status.HTTP_200_OK)
        else:
            return Response({'result': 'fail', 'message': 'Vertiport name is required.'}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    def get(self, request):
        try:
            # refresh token으로 access token 재발급
            serializer = self.get_serializer(data={'refresh': request.COOKIES.get('refresh')})

            if serializer.is_valid():
                access_token = serializer.validated_data

                res = Response(
                    {
                        'result': 'success',
                        'data': {
                            'token': access_token
                        }
                    },
                    status=status.HTTP_200_OK,
                )

                # 재발급한 access token을 쿠키에 저장
                res.set_cookie('access', access_token['access'], httponly=True, secure=True, samesite='None')
                return res
            else:
                raise Exception('There is no refresh in cookie')
        except Exception as e:
            return Response({'result': 'fail', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
