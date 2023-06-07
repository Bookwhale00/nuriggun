from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404

from .models import User

from user.serializers import (
    SubscribeSerializer,
)


class UserView(APIView):
    def post(self, request):
        pass
    def put(self, request):
        pass
    def delete(self,request):
        pass
        

# ----- 구독 시작 -----

class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 구독 등록/취소
    def post(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        me = request.user
        if you != me:
            if me in you.subscribes.all():
                you.subscribes.remove(me)
                return Response("구독 취소", status=status.HTTP_205_RESET_CONTENT)
            else:
                you.subscribes.add(me)
                return Response("구독 완료", status=status.HTTP_200_OK)
        else:
            return Response("자신을 구독 할 수 없습니다.", status=status.HTTP_403_FORBIDDEN)

    # 구독 리스트
    def get(self, request, user_id):
        subscribes = User.objects.filter(id=user_id)
        subscribes_serializer = SubscribeSerializer(subscribes, many=True)
        return Response(
            {
                "subscribe": subscribes_serializer.data
            }
        )
    
# ----- 구독 끝 -----