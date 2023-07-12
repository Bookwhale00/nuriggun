import os
import logging

def setup_logger():
    # 로그 생성 (모듈 이름으로 표시)
    logger = logging.getLogger(__name__)

    # 로그 출력 레벨 설정
    logger.setLevel(logging.INFO)

    # 로그 출력 형식
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 콘솔 출력(+포매터)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # 파일 로그 기록(+포매터)
    file_handler = logging.FileHandler('./weather/weather.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger