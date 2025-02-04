from django.urls import path
from .views import *

urlpatterns = [
    path('register', RegistrationView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('exercises', ExerciseView.as_view(), name='exercises'),
    path('user-plan', UserPlanView.as_view(), name='set-get_plan'),
    path('workout', WorkoutView.as_view(), name='workout-mode'),
    path('tracker', UserTrackView.as_view(), name='tracker'),
]
