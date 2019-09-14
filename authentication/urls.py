from django.urls import path

from applibs.custom_login import get_jwt_token_for_login_user, refresh_jwt_token
from authentication import views

urlpatterns = [

	# JWT auth token
	path('token/', get_jwt_token_for_login_user, name='token_obtain'),
    path('token/refresh/', refresh_jwt_token, name='token_refresh'),

    # app routs
    path('login/', views.UserLoginView.as_view(), name='home'),
    path('account/verification/<slug:uuid>/<slug:token>/', views.UserVerificationView.as_view()),
]
