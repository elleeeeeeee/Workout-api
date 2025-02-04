from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from .serializer import UserSerializer, ExerciseSerializer, WorkoutSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Exercises, UserPlan, ExerciseStatus
from django.core.exceptions import ObjectDoesNotExist
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



""" Authentication/Registration/Logout Views """

class RegistrationView(APIView):
    @swagger_auto_schema(
        operation_description="Register",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, example="string"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, example="string"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, example="string"),
                'weight': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                'age': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                'height': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
            },
            required=['username', 'password', 'email', 'weight', 'age', 'height']
        ),
        responses={201: openapi.Response("Workout plan deleted successfully")}
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "User created successfully"})


#########################
class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Register",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, example="string"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, example="string")
            },
            required=['username', 'password']
        ),
        responses={201: openapi.Response("Workout plan deleted successfully")}
    )
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed("User not found!")
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")

        refresh = RefreshToken.for_user(user)

        response = Response()

        response.set_cookie(key='jwt', value=str(refresh.access_token), httponly=True)
        response.data = {
            "jwt": str(refresh.access_token),
            'refresh': str(refresh),
        }

        return response


#########################
class LogoutView(APIView):
    def post(self, request):
        if request.COOKIES.get('jwt') is not None:

            response = Response()
            response.delete_cookie('jwt')
            response.data = {
                'message': 'Successfully logged out'
            }
            return response
        else:
            return Response({'message': 'Not authenticated'})


#########################

""" Exercise View """


class ExerciseView(APIView):
    def get(self, request):
        exercises = Exercises.objects.all()

        return Response(ExerciseSerializer(exercises, many=True).data)


""" User Plan View """
class UserPlanView(APIView):
    @swagger_auto_schema(
        operation_description="User plan",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'goals': openapi.Schema(type=openapi.TYPE_STRING, example="string"),
                'exercise_type': openapi.Schema(type=openapi.TYPE_STRING, example="string"),
                'exercises': openapi.Schema(type=openapi.TYPE_ARRAY, items=["exercise_name", "exercise_name"]),
                'daily_duration': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                'frequency': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
            },
            required=['goals', 'exercise_type', 'exercises', 'daily_duration', 'frequency']
        ),
        responses={201: openapi.Response("Workout plan added successfully")}
    )
    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated user!")
        try:
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated user!")

        user = User.objects.filter(pk=payload['user_id']).first()

        exercises = request.data['exercises']
        frequency = request.data['frequency']
        goals = request.data['goals']
        exercise_type = request.data['exercise_type']
        daily_duration = request.data['daily_duration']

        if UserPlan.objects.filter(user=user):
            return Response({'message': 'User plan already exists!'})

        user_choice = UserPlan.objects.create(user=user,
                                              frequency=frequency,
                                              goals=goals,
                                              exercise_type=exercise_type,
                                              daily_duration=daily_duration)
        exercises_lst = []
        for exercise in exercises:
            try:
                ex = Exercises.objects.get(name__contains=exercise)
                user_choice.exercises.add(ex)

                ExerciseStatus.objects.create(user=user, exercise=ex).save()

                ex_status_obj = ExerciseStatus.objects.get(user=user, exercise=ex)
                user_choice.exercises_status.add(ex_status_obj)

            except ObjectDoesNotExist:
                exercises_lst.append(exercise)
        user_choice.save()

        if len(exercises_lst) == 0:
            return Response({"message": f"User plan added successfully!"})
        else:
            return Response(
                {"message": f"User plan added successfully! but {exercises_lst} not added because we can't find it"})

    @swagger_auto_schema(
        operation_description="User plan",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'goals': openapi.Schema(type=openapi.TYPE_STRING, example="string"),
                'exercise_type': openapi.Schema(type=openapi.TYPE_STRING, example="string"),
                'exercises': openapi.Schema(type=openapi.TYPE_ARRAY, items=["exercise_name", "exercise_name"]),
                'daily_duration': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                'frequency': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
            },
            required=['goals', 'exercise_type', 'exercises', 'daily_duration', 'frequency']
        ),
        responses={201: openapi.Response("Workout plan updated successfully")}
    )
    def put(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated user!")
        try:
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated user!")

        user = User.objects.filter(pk=payload['user_id']).first()

        exercises = request.data['exercises']
        frequency = request.data['frequency']
        goals = request.data['goals']
        exercise_type = request.data['exercise_type']
        daily_duration = request.data['daily_duration']

        user_choice = UserPlan.objects.get(user=user)

        user_choice.frequency = frequency
        user_choice.goals = goals
        user_choice.exercise_type = exercise_type
        user_choice.daily_duration = daily_duration

        exercises_lst = []
        for exercise in exercises:
            try:
                ex = Exercises.objects.get(name__contains=exercise)
                ex_status = ExerciseStatus.objects.filter(user=user, exercise=ex)
                if not ex_status:
                    ExerciseStatus.objects.create(user=user, exercise=ex).save()

                ex_status_obj = ExerciseStatus.objects.get(user=user, exercise=ex)
                user_choice.exercises_status.add(ex_status_obj)
                user_choice.exercises.add(ex)
            except ObjectDoesNotExist:
                exercises_lst.append(exercise)
        user_choice.save()

        if len(exercises_lst) == 0:
            return Response({"message": f"User plan updated successfully!"})
        else:
            return Response(
                {"message": f"User plan updated successfully! but {exercises_lst} not added because we can't find it"})


""" Workout mode view """

class WorkoutView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated user!")
        try:
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated user!")

        user = User.objects.filter(pk=payload['user_id']).first()

        user_plan = UserPlan.objects.filter(user=user)

        return Response(WorkoutSerializer(user_plan, many=True).data)

    @swagger_auto_schema(
        operation_description="User plan",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'exercise': openapi.Schema(type=openapi.TYPE_STRING, example="Plank"),
                'is_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN, example="true"),
            },
            required=['exercise', 'is_completed']
        ),
        responses={201: openapi.Response("User plan updated successfully")}
    )
    def put(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated user!")
        try:
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated user!")

        user = User.objects.filter(pk=payload['user_id']).first()

        exercise = request.data['exercise']
        is_completed = request.data['is_completed']
        exercise_obj = Exercises.objects.get(name__contains=exercise)
        exercise_status = ExerciseStatus.objects.get(user=user, exercise=exercise_obj)

        if exercise_obj:

            exercise_status.status = is_completed
            exercise_status.save()
        else:
            raise ObjectDoesNotExist("This exercise does not exist!")

        return Response({"message": "Completed exercises added successfully!"})


""" User Tracker View """
class UserTrackView(APIView):
    @swagger_auto_schema(
        operation_description="User plan",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'weight_now': openapi.Schema(type=openapi.TYPE_INTEGER, example=100),
                'goal_weight': openapi.Schema(type=openapi.TYPE_INTEGER, example=90),
            },
            required=['weight_now', 'goal_weight']
        ),
        responses={201: openapi.Response("Tracker updated successfully")}
    )
    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated user!")
        try:
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated user!")

        user = User.objects.filter(pk=payload['user_id']).first()

        weight_now = request.data['weight_now']
        goal_weight = request.data['goal_weight']

        old_weight = user.weight

        weight_difference = old_weight - weight_now
        goal_difference = weight_now - goal_weight

        if weight_difference < 0:
            message = "Your have gained weight! Please review your diet and exercises."
        elif goal_weight == weight_now:
            message = f"You reached your goal! Your weight is {goal_weight}"
        elif 0 < weight_difference <= goal_difference:
            message = f"You lost {weight_difference} kg! Keep it up! ☺ you are closer to your dream!"
        else:
            message = "Your weight does not change! Please review exercises and diet."

        user.weight = weight_now
        user.save()

        return Response({'message': message})

