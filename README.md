# ETL Project
This is  a learning project. An application loads the csv-file, filters the data and the saves result to a new file.

##Project build:
### 1. Настройка переменных окружения
Скопируйте файл с примером конфигурации:
```bash
copy .env.example .env

    docker build -t etl_project .

Project run:

    docker run etl_project 