# Music Stream Service

Music Stream Service - это музыкальный стриминговый сервис.

## Установка и запуск
Установка нужных пакетов:
```
sudo apt update
sudo apt upgrade
sudo apt install git screen python3 python3-pip python3-venv postgresql postgresql-contrib
```

```
git clone https://github.com/Explorer-art/music-stream-service.git
cd music-stream-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### API
##### Поиск треков
```
GET /api/tracks/search?query=Название

HTTP Header
Authorization: TOKEN
```

##### Добавить новый трек
```
POST /api/tracks/upload

HTTP Header
Authorization: TOKEN
```

##### Удалить трек
```
DELETE /api/tracks/{track_id}

HTTP Header
Authorization: TOKEN
```

##### Получить список треков
```
GET /api/tracks

HTTP Header
Authorization: TOKEN
```

##### Получить информацию о треке
`GET /api/tracks/{track_id}`

##### Получить картинку трека
`GET /api/tracks/{track_id}/image`

##### Прослушать трек
`GET /api/tracks/{track_id}/stream`