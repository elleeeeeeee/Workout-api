from django.contrib import admin
from .models import User, Exercises, UserPlan, ExerciseStatus

admin.site.register(User)
admin.site.register(Exercises)
admin.site.register(UserPlan)
admin.site.register(ExerciseStatus)
