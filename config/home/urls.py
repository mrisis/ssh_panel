from django.urls import path
from .views import LoginView, CreateUserView, DeleteUserView, HomeView, LogoutView

urlpatterns = [

    path('login/', LoginView.as_view(), name="login"),
    path('create_user/', CreateUserView.as_view(), name="create_user"),
    path('delete_user/', DeleteUserView.as_view(), name="delete_user"),
    path('home/', HomeView.as_view(), name='home'),
    path('logout/', LogoutView.as_view(), name="logout"),

]