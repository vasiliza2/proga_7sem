import json
import os
from requests_oauthlib import OAuth2Session
import sys

def load_config(path="config.json"):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for k, v in data.items():
            os.environ.setdefault(k, str(v))

# Загружаем конфиг
load_config("config.json")

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = "https://localhost:8000/callback" # Должен совпадать с тем, что вы указали на GitHub
AUTHORIZATION_BASE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"
SCOPE = ["read:user,user:email"]


oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)

# Генерируем URL авторизации
authorization_url, state = oauth.authorization_url(AUTHORIZATION_BASE_URL)

print("Перейдите по ссылке для авторизации:", authorization_url)
print("(Этот скрипт будет ждать, пока вы не вставите URL перенаправления)")

redirect_response = input("Вставьте полный URL перенаправления из браузера: ")

# Обмениваем авторизационный код на access token
try:
    token = oauth.fetch_token(
        TOKEN_URL,
        authorization_response=redirect_response,
        client_secret=CLIENT_SECRET
    )
    print("Access Token:", token)
except Exception as e:
    print(f"Ошибка при получении токена: {e}")
    sys.exit(1)

#  Используем полученный токен для запроса защищенного ресурса
try:
    print("\nЗапрашиваем данные пользователя GitHub...")
    r = oauth.get("https://api.github.com/user")
    r.raise_for_status() # Вызывает исключение для плохих статусов HTTP (4xx или 5xx)

    user_data = r.json()
    print("\nВаши данные с GitHub:")
    print(f"Имя пользователя (login): {user_data.get('login')}")
    print(f"Отображаемое имя (name): {user_data.get('name')}")
    print(f"Email: {user_data.get('email', 'Не указан или нет доступа (проверьте scope user:email)')}")
    print(f"URL профиля: {user_data.get('html_url')}")
    # print("\nПолный JSON ответ:", user_data) # Раскомментируйте для полного ответа
    
except Exception as e:
    print(f"\nОшибка при получении данных пользователя: {e}")