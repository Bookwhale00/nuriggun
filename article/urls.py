from django.urls import path, include
from article import views

urlpatterns = [

    path("", views.ArticleView.as_view(), name="article_view"),
    path("<int:article_id>/",views.ArticleDetailView.as_view(),name="article_detail_view"),
    path("list/<int:user_id>/", views.ArticleListView.as_view(), name="article_list"),
    # path("<int:article_id>/comment/", views.CommentView.as_view(), name="comment_view"),
    path('scrap/', views.ScrapListView.as_view(),name='scrap_view'),  # 북마크 한 게시글
    path('<int:article_id>/scrap/', views.ScrapView.as_view(),name='scrap_view'),  # 북마크 기능
]

