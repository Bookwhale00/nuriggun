from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from article.models import Article, Comment
from article.serializers import (
    ArticleSerializer,
    ArticleCreateSerializer,
    ArticlesUpdateSerializer,
    CommentSerializer,
    CommentCreateSerializer)
import datetime
from rest_framework import permissions

from user.models import User


#------------------------------------- 게시글 생성 ------------------------------------- 

class ArticleView(APIView): 
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
# ------------------------------------ 게시글 목록 -------------------------------------
    
    def get(self, request):  
        category = request.GET.get('category')

        if category:  
            articles = Article.objects.filter(category=category) # 카테고리 있는 경우 해당 카테고리의 게시글 보여줌
        else:  
            articles = Article.objects.all()# 카테고리 없는 경우 모든 게시글 보여주기

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ------------------------------------- 게시글 작성 -------------------------------------

    def post(self, request): 
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------- 게시글 리스트 보기 -------------------------------------      


class ArticleListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  
    
    def get(self, request, user_id):  
        articles = Article.objects.filter(user_id=user_id)
        serializer = ArticleSerializer(articles, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

# ------------------------------------- 게시글 상세페이지 -------------------------------------      
