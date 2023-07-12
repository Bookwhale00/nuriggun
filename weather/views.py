from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import WeatherCity, WeatherData
from .serializers import WeatherDataSerializer

class WeatherView(APIView):
    '''날씨 데이터 DB->클라이언트 전송'''
    def get(self, request):
        cities = WeatherCity.objects.all()
        weather = []
        
        for city in cities:
            latest_weather = WeatherData.objects.filter(city=city).order_by('-timestamp').first()

            if latest_weather is not None:
                weather.append(latest_weather)
        
        serializer = WeatherDataSerializer(weather, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
