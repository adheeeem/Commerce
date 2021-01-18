from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("items/<int:listing_id>", views.items, name="items"),
    path("watchlists", views.watchlists, name="watchlists"),
    path("category", views.category, name="category"),
    path("category/<str:ex_category>", views.exact_category, name="exact_category")
]


