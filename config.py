# config.py
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일에서 환경변수 로드

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
TOKEN = os.getenv("TOKEN")