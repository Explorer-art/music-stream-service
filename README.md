# Music Stream Service

Music Stream Service - это музыкальный стриминговый сервис.

### Установка и запуск
```
git clone https://github.com/Explorer-art/music-stream-service.git
sudo docker build -t music-service-image
sudo docker run -d --name music-service-docker -p 8000:8000 music-service-image
```

### API
##### Поиск треков
**GET** `/api/tracks/search?query=Название`

##### Добавить новый трек
**POST** `/api/tracks/upload`

##### Удалить трек
**DELETE** `/api/tracks/{track_id}`

##### Получить список треков
**GET** `/api/tracks`

##### Получить информацию о треке
**GET** `/api/tracks/{track_id}`

##### Получить миниатюру картинки трека
**GET** `/api/tracks/{track_id}/thumbnail`

##### Получить картинку трека
**GET** `/api/tracks/{track_id}/image`

##### Прослушать трек
**GET** `/api/tracks/{track_id}/stream`