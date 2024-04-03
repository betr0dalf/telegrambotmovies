import requests

headers = {
    'X-API-KEY': '096e8092-9c8a-45f4-9a8f-a90339f0472d',
    'Content-Type': 'application/json'
}

response = requests.get('https://kinopoiskapiunofficial.tech/api/v2.2/films/301', headers=headers)

if response.status_code == 200:
    print(response.json())
else:
    print(f'Ошибка {response.status_code}: {response.text}')
