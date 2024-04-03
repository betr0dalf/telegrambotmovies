import requests

headers = {
    'X-API-KEY': '096e8092-9c8a-45f4-9a8f-a90339f0472d', # Api кей свой сделай по ссылке https://kinopoiskapiunofficial.tech/
    'Content-Type': 'application/json'
}

my_file = open("data.txt", "a+")

# 341 строка баг выдаёт. Надо проверить с какого фильмы начинаются (c 0 до 301 пройтись, возможно там раньше что-то было)
# Также я создал заранее файл data.txt Не уверен что он в режиме a+ сразу нормально заработает
# Файл data.txt заполнен с 301 по 340
for movie_id in range(340, 1001):
    response = requests.get('https://kinopoiskapiunofficial.tech/api/v2.2/films/' + str(movie_id), headers=headers)
    if response.status_code == 200:
        print(response.json())
        my_file.write(str(response.json()) + '\n')
    else:
        print(f'Ошибка {response.status_code}: {response.text}')
my_file.close()
