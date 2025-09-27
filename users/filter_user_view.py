from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer
from .models import CustomUser
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView


class UserFilterView(GenericAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_summary="Admin can only view all users here with optional filtering by first_name, last_name, email",
        manual_parameters=[
            openapi.Parameter(
                'first_name',
                openapi.IN_QUERY,
                description="Serach by first name",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'last_name',
                openapi.IN_QUERY,
                description="Serach by last name",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'email',
                openapi.IN_QUERY,
                description="Serach by email",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: UserSerializer(many=True), 403: "Forbidden"}    
    )
    def get(self, request):
        users = CustomUser.objects.filter(is_active=True)

        fname = request.query_params.get('first_name')
        lname = request.query_params.get('last_name')
        email = request.query_params.get('email')

        if fname:
            users = users.filter(first_name__contains=fname)
        if lname:
            users = users.filter(last_name__contails=lname)
        if email:
            users = users.filter(email=email)

        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)