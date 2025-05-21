import requests

# Пример создания объявления
advert_data = {
    "title": "Объявление1",
    "description": "Описание объявления",
    "owner_id": "777"
}

API_URL = 'http://127.0.0.1:8080/api/v1/adverts'
#
# # Создание объявления
# response = requests.post(API_URL, json=advert_data)
# print('POST /adverts', response.status_code, response.json())
#
# Получение списка всех объявлений
response = requests.get(API_URL)
print('GET /adverts', response.status_code, response.json())

# Получение конкретного объявления (предположим, с ID 1)
response = requests.get(f'{API_URL}/1')
print('GET /adverts/1', response.status_code, response.json())