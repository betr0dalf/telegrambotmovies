import requests
import pandas as pd


headers = {
    'X-API-KEY': '096e8092-9c8a-45f4-9a8f-a90339f0472d',
    # Api кей свой сделай по ссылке https://kinopoiskapiunofficial.tech/
    'Content-Type': 'application/json'
}

# my_file = open("data.txt", "a+")
#
# # 341 строка баг выдаёт. Надо проверить с какого фильмы начинаются (c 0 до 301 пройтись, мб там раньше что-то было)
# # Также я создал заранее файл data.txt Не уверен что он в режиме a+ сразу норм заработает
# # Файл data.txt заполнен с 301 по 340
# for movie_id in range(298, 1001):
#     response = requests.get('https://kinopoiskapiunofficial.tech/api/v2.2/films/' + str(movie_id), headers=headers)
#     if response.status_code == 200:
#         print(response.json())
#         my_file.write(str(response.json()) + '\n')
#     else:
#         print(f'Ошибка {response.status_code}: {response.text}')
# my_file.close()

KPid = []  # ID КИНОПОИСК
NameFilm = []  # Название на русскому
NameFilmEn = []  # Название на английском
PosterUrl = []  # Фулл картинка
PosterUrlSmall = []  # Уменьшенная картинка
Description = []  # Описание
Countries = []  # Страна
ratingMpaa = []  # Возрастное ограничение
ratingAgeLimits = []  # Возрастное ограничение
Type = []  # Фильм или сериал
Year = []  # Год выпуска
Genres = []  # Жанры
ratingImdb = []  # Рейтинг Imdb
ratingKP = []  # Рейтинг Кинопоиска
AverageRating = []  # Рекомендательный рейтинг
filmLength = []  # Длительность в минутах
WebUrl = []  # https://w2.kpfr.wiki/film/ ссылка на просмотр
Genres1 = []
WebUrl2 = []
WeightKP = 0
WeightImdb = 0
for i in range(298, 500):
    response = requests.get('https://kinopoiskapiunofficial.tech/api/v2.2/films/' + str(i), headers=headers)
    Str = response.json()

    ratingKinopoiskVoteCount = 1
    ratingImdbVoteCount = 1
    ratingFilmCritics = 1
    ratingFilmCriticsVoteCount = 1
    for section, command in Str.items():
        print(section, command)
        if section == "kinopoiskId":
            KPid.append(command)
        if section == "nameRu":
            NameFilm.append(command)
        if section == "nameEn":
            NameFilmEn.append(command)
        if section == "posterUrl":
            PosterUrl.append(command)
        if section == "posterUrlPreview":
            PosterUrlSmall.append(command)
        if section == "ratingKinopoisk":
            ratingKP.append(command)
        if section == "ratingImdb":
            ratingImdb.append(command)
        if section == "ratingFilmCritics":
            ratingFilmCritics = command
        if section == "ratingKinopoiskVoteCount":
            ratingKinopoiskVoteCount = command
        if section == "ratingImdbVoteCount":
            ratingImdbVoteCount = command
        if section == "ratingFilmCriticsVoteCount":
            ratingFilmCriticsVoteCount = command
        if section == "year":
            Year.append(command)
        if section == "filmLength":
            filmLength.append(command)
        if section == "description":
            Description.append(command)
        if section == "ratingMpaa":
            ratingMpaa.append(command)
        if section == "ratingAgeLimits":
            ratingAgeLimits.append(command)
        if section == "countries":
            Genres1 = ((str(command).replace("country", "").
                        replace(" ", "").replace("'", "").
                        replace("{", "").replace(":", "")).
                       replace("[", "").replace("}", "")).replace("]", "").split(",")
            Countries.append(Genres1)
        if section == "genres":
            Genres1 = ((str(command).replace("genre", "").
                        replace(" ", "").replace("'", "").
                        replace("{", "").replace(":", "")).
                       replace("[", "").replace("}", "")).replace("]", "").split(",")
            Genres.append(Genres1)
        if section == "type":
            Type.append(command)
        if section == "webUrl":
            WebUrl2.append(command)

        VoteCount = ratingImdbVoteCount + ratingKinopoiskVoteCount + ratingFilmCriticsVoteCount * 1000
        if len(ratingKP) > 0:
            WeightKP = VoteCount / ratingKinopoiskVoteCount * ratingKP[-1]
        if len(ratingImdb) > 0:
            WeightImdb = VoteCount / ratingImdbVoteCount * ratingImdb[-1]
        WeightCritics = VoteCount / ratingFilmCriticsVoteCount * ratingFilmCritics

        WebUrl.append("https://w2.kpfr.wiki/film/" + str(i))
        AverageRating.append(WeightKP + WeightCritics + WeightImdb)

    data = {'KPid': KPid,
            'Type': Type,
            'NameFilm': NameFilm,
            'NameFilmEn': NameFilmEn,
            'Year': Year,
            'Countries': Countries,
            'Genres': Genres,
            'ratingKP': ratingKP,
            'ratingImdb': ratingImdb,
            'AverageRating': AverageRating,
            'ratingMpaa': ratingMpaa,
            'ratingAgeLimits': ratingAgeLimits,
            'Description': Description,
            'WebUrl': WebUrl,
            'WebUrl2': WebUrl2
            }

    df = pd.DataFrame(data)
    df.to_csv('output.csv', index=False)

    # print(KPid, Type, NameFilm, NameFilmEn, Year, Countries, Genres,
    # ratingKP, ratingImdb, AverageRating, ratingMpaa, ratingAgeLimits, Description, WebUrl)