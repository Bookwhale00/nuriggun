import os
import requests
from .models import WeatherCity, WeatherData
from datetime import date, datetime, timedelta
from urllib.parse import urlencode, quote_plus, unquote
from .serializers import WeatherDataSerializer
from django.http import JsonResponse
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import time
import logging
from .weather_logging_config import setup_logger

logger = setup_logger()

MAX_RETRIES = 3

def load_weather(nx, ny):
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

            serviceKey = os.environ.get('WEATHER_API_KEY')
            serviceKeyDecoded = unquote(serviceKey, 'UTF-8')

            now = datetime.now()
            today = datetime.today().strftime("%Y%m%d")
            y = date.today() - timedelta(days=1)
            yesterday = y.strftime("%Y%m%d")

            pre_hour = (now.hour - 1) if now.hour != 0 else 23
            if pre_hour < 10:  
                base_time = "0" + str(pre_hour) + "30"
            else:
                base_time = str(pre_hour) + "30"

            if now.hour == 0:
                base_date = yesterday
            else:
                base_date = today

            queryParams = '?' + urlencode({ quote_plus('serviceKey') : serviceKeyDecoded, quote_plus('base_date') : base_date,
                                            quote_plus('base_time') : base_time, quote_plus('nx') : nx, quote_plus('ny') : ny,
                                            quote_plus('dataType') : 'json', quote_plus('numOfRows') : '1000'})
            
            res = requests.get(url + queryParams, verify=False)

            items = res.json().get('response').get('body').get('items')

            data = dict()

            data['date'] = base_date

            weather_data = dict()

            for item in items['item']:
                # 기온
                if item['category'] == 'T1H':
                    weather_data['tmp'] = item['obsrValue']
                # 습도
                if item['category'] == 'REH':
                    weather_data['hum'] = item['obsrValue']
                # 강수타입: 없음(0), 비(1), 비/눈(2), 눈(3), 빗방울(5), 빗방울눈날림(6), 눈날림(7)
                if item['category'] == 'PTY':
                    weather_data['sky'] = item['obsrValue']
                # 1시간 동안 강수량
                if item['category'] == 'RN1':
                    weather_data['rain'] = item['obsrValue']

            logger.info(f"날씨정보 요청 성공 : {weather_data}")
            return weather_data
    
        except requests.exceptions.RequestException as e:
            logger.error(f"요청 중 에러 발생 : {e}")

        except ValueError:
            logger.error(f"데이터를 불러오지 못함 nx={nx}, ny={ny} \n응답 : {res.text}")

        except Exception as e:
            logger.error(f"알 수 없는 에러 발생: {e}")
        
        logger.info(f"에러 발생. {retry_count+1} 번째 재시도합니다.")
        time.sleep(2)  
        retry_count += 1

    logger.info(f"최대 재시도 횟수를 초과했습니다. nx={nx}, ny={ny}")
    return None

def save_weather():
    cities = WeatherCity.objects.all()

    if not cities:
        logger.info("지역정보가 없습니다.")
        return
    
    for city in cities:

        weather_data = load_weather(city.nx, city.ny)

        if weather_data is None:
            logger.info(f"{city}지역 날씨 데이터를 불러오는 데 실패했습니다.")
            continue

        try:
            weather_data_instance = WeatherData.objects.create(
                city = city,
                timestamp = datetime.now(),  
                temp = weather_data['tmp'],
                humidity = weather_data['hum'],
                rain = weather_data['rain'],
                sky = weather_data['sky'],
            )
        except UnboundLocalError as e:
            logger.error("날씨데이터 생성 에러: ", e)
            continue
        
    serializer = WeatherDataSerializer(weather_data_instance)
    return JsonResponse(serializer.data, safe=False)
        
def delete_weather():
    '''어제 혹은 어제보다 이전 날씨 데이터 삭제'''
    today = timezone.localtime(timezone.now())
    yesterday = today.replace(hour=23, minute=59, second=59, microsecond=0) - timedelta(days=1)
    logger.info("날씨정보 삭제")
    WeatherData.objects.filter(timestamp__lte=yesterday).delete()

def cron_weather():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_weather, 'cron', hour='21', minute='17', id='cron_delete_weather')
    scheduler.add_job(save_weather, 'cron', hour='0,2,4,6,8,10,12,14,16,18,20,21,22', minute='29', id='cron_save_weather')
    scheduler.start()
