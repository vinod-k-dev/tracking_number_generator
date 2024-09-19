from django.db import IntegrityError, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.utils.text import slugify
from uuid import UUID, uuid4
from tracking.serializers import TrackingNumberSerializer
from tracking.models import TrackingNumber
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
class TrackingNumberView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('origin_country_id', openapi.IN_QUERY, description="Origin Country Code", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('destination_country_id', openapi.IN_QUERY, description="Destination Country Code", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('weight', openapi.IN_QUERY, description="Weight in kilograms (up to 3 decimal places)", type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter('customer_id', openapi.IN_QUERY, description="Customer UUID", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('customer_name', openapi.IN_QUERY, description="Customer Name", type=openapi.TYPE_STRING, required=True),
        ],
        responses={201: openapi.Response('Success', examples={
            "application/json": {
                "tracking_number": "A1B2C3D4E5F6G7H8",
                "created_at": "2023-09-12T12:30:00+00:00"
            }
        })}
    )
    def get(self, request):
        # Extract and validate query parameters
        required_params = ['origin_country_id', 'destination_country_id', 'weight', 'customer_id', 'customer_name']
        data = {param: request.query_params.get(param) for param in required_params}

        # Check for missing required parameters
        missing_params = [param for param, value in data.items() if value is None]
        if missing_params:
            return Response(
                {"error": f"Missing required query parameters: {', '.join(missing_params)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate and format parameters
        try:
            data['weight'] = float(data['weight'])
            data['customer_id'] = UUID(data['customer_id'])
            data['created_at'] = request.query_params.get('created_at', timezone.now())
            data['customer_slug'] = slugify(data['customer_name']) if not request.query_params.get('customer_slug') else request.query_params.get('customer_slug')
        except (ValueError, TypeError) as e:
            return Response(
                {"error": f"Invalid data types: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate a unique tracking number with concurrency handling
        try:
            with transaction.atomic():
                data['tracking_number'] = self.generate_unique_tracking_number(data['origin_country_id'], data['destination_country_id'], data['weight'], data['customer_id'])

                # Save the tracking number to the database
                tracking_record = TrackingNumber.objects.create(**data)

        except IntegrityError:
            return Response(
                {"error": "A unique tracking number could not be generated due to a collision. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Prepare the response data
        response_data = {
            "tracking_number": tracking_record.tracking_number,
            "created_at": tracking_record.created_at.isoformat()
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    def generate_unique_tracking_number(self, origin_country_id, destination_country_id, weight, customer_id):
        """Generates a unique tracking number following the pattern ^[A-Z0-9]{1,16}$."""
        for attempt in range(10):  # Retry up to 10 times in case of a collision
            # Generate a 16-character tracking number
            tracking_number = f'{origin_country_id[:2].upper()}{destination_country_id[:2].upper()}{str(int(weight * 1000)).zfill(4)}{uuid4().hex[:8].upper()}'
            
            # Trim to ensure it's no longer than 16 characters
            tracking_number = tracking_number[:16]
            
            # Check for uniqueness and return if it doesn't exist
            if not TrackingNumber.objects.filter(tracking_number=tracking_number).exists():
                return tracking_number
        
        # If a unique number isn't generated after 10 tries, raise an error
        raise IntegrityError("Unable to generate a unique tracking number.")

class TrackingNumberListView(APIView):

    @swagger_auto_schema(
        responses={200: TrackingNumberSerializer(many=True)}
    )
    def get(self, request):
        tracking_numbers = TrackingNumber.objects.all()
        serializer = TrackingNumberSerializer(tracking_numbers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)