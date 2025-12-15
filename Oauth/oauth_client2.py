import json
import requests
import time
import os
from google_auth_oauthlib.flow import Flow
from requests.exceptions import RequestException


# Имя файла с вашими учетными данными OAuth, загруженное из Google Cloud Console
CLIENT_SECRET_FILE = './client_secret.json'
# Области доступа (Scopes), которые вы запрашиваете
SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'openid']
# URI перенаправления, который должен совпадать с URI, указанным в Google Cloud Console
# Рекомендуется использовать HTTPS, но для run_local_server() часто нужен HTTP
REDIRECT_URI = 'https://localhost:8080/auth/google/callback' 
TOKEN_URI = 'https://oauth2.googleapis.com/token'


def run_oauth_flow_and_get_credentials():
    """
    Выполняет шаги OAuth 2.0 Flow для получения учетных данных.
    Использует ручной ввод URL для совместимости.
    """
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"Ошибка: Файл учетных данных '{CLIENT_SECRET_FILE}' не найден.")
        print("Убедитесь, что вы скачали 'client_secret.json' из Google Cloud Console и поместили его рядом со скриптом.")
        return None
        
    try:
        # 1. Инициализация Flow
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

        # 2. Генерация URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',  # Ключевой параметр для получения Refresh Token
            include_granted_scopes='true'
        )

        print('=' * 60)
        print('Шаг 1: Авторизация пользователя')
        print(f'Пожалуйста, перейдите по следующей ссылке для авторизации:\n{authorization_url}')
        print('=' * 60)

        # 3. Ожидание ввода от пользователя
        authorization_response = input('Вставьте сюда ПОЛНЫЙ URL-адрес перенаправления (включая state и code): ')

        # 4. Обмен токенами
        print('\nШаг 2: Обмен кода авторизации на токены...')
        flow.fetch_token(authorization_response=authorization_response)
        
        return flow.credentials

    except Exception as e:
        print(f"\n Критическая ошибка в процессе авторизации: {e}")
        print("Проверьте URI перенаправления и наличие параметров 'state'/'code' в скопированном URL.")
        return None

def fetch_user_info(access_token):
    """Тестовый запрос к API информации о пользователе для проверки Access Token."""
    USER_INFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("\n--- Проверка Access Token (Запрос к UserInfo API) ---")
    try:
        response = requests.get(USER_INFO_URL, headers=headers)
        response.raise_for_status() 
        user_data = response.json()
        
        print(" Запрос к API успешен. Получены данные:")
        print(json.dumps(user_data, indent=4))
        
    except RequestException as e:
        print(f" Ошибка при запросе данных пользователя: {e}")

def refresh_access_token(client_id, client_secret, refresh_token):
    """
    Использует Refresh Token для получения нового Access Token.
    """
    print("\n--- Шаг 3: Демонстрация обновления Access Token ---")
    
    if not refresh_token:
        print(" Обновление невозможно: Refresh Token отсутствует в учетных данных.")
        return None

    payload = {
        'grant_type': 'refresh_token',
        'client_secret': client_secret, 
        'refresh_token': refresh_token, 
        'client_id': client_id,
    }
    
    try:
        response = requests.post(TOKEN_URI, data=payload)
        response.raise_for_status() 
        
        token_data = response.json()
        new_access_token = token_data.get('access_token')

        print("Успешное обновление.")
        print(f"   Получен НОВЫЙ Access Token: {new_access_token[:30]}...")
        print(f"   Срок действия: {token_data.get('expires_in')} секунд.")
        return new_access_token

    except RequestException as e:
        print(f" Ошибка при обновлении токена: {e}")
        return None

# --- ГЛАВНАЯ ФУНКЦИЯ СКРИПТА ---

if __name__ == '__main__':
    # 1. Получение учетных данных
    credentials = run_oauth_flow_and_get_credentials()

    if credentials:
        # 2. Извлечение необходимых данных
        credentials_dict = json.loads(credentials.to_json())

        REFRESH_TOKEN = credentials_dict.get('refresh_token')
        ACCESS_TOKEN = credentials_dict.get('token')
        CLIENT_ID = credentials_dict.get('client_id')
        CLIENT_SECRET = credentials_dict.get('client_secret')

        print('\n' + '=' * 60)
        print('Успешно получены учетные данные:')
        print(f"  Access Token: {ACCESS_TOKEN[:10]}...")
        # Условная печать: обрезаем токен, только если он существует
        print(f"  Refresh Token: {REFRESH_TOKEN[:10] + '...' if REFRESH_TOKEN else 'НЕ ПОЛУЧЕН (сохраните предыдущий!)'}")
        print(f"  Client ID: {CLIENT_ID}")
        print('=' * 60)

        # 3. Проверка текущего Access Token
        if ACCESS_TOKEN:
            fetch_user_info(ACCESS_TOKEN)

        # 4. Демонстрация обновления токена (используется REFRESH_TOKEN)
        refresh_access_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)

