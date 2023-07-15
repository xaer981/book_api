# Book API
This project allow to add .epub books (they will be handled and added to DB (book name, author name, names and texts of chapters)), search in book with query, returning cutted fragment of found text.

## Quick overview
Project using:
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL as DB
* Redis as cache (with [fastapi-cache](https://github.com/long2ice/fastapi-cache) by [long2ice](https://github.com/long2ice))
* Pagination system ([fastapi-pagination](https://github.com/uriyyo/fastapi-pagination) by [uriyyo](https://github.com/uriyyo))
* Managing .epub books lib ([ebooklib](https://github.com/aerkalov/ebooklib) by [aerkalov](https://github.com/aerkalov))
* Docker + docker-compose

## Installation guide
1. Clone current repo: ```git clone https://github.com/xaer981/book_api.git```
2. Go to the new dir and create .env file from example: ```cd book_api/ && cp default.env .env```
   * ADMIN_USER - username for using in basic auth to add new books to DB
   * ADMIN_PASSWORD - password for using in basic auth to add new books to DB
   * DB_URL - default url to get access to DB from FastAPI(```postgresql://postgres:postgres@book_api-db/{name of DB}```)
   * POSTGRES_USER
   * POSTGRES_PASSWORD
   * POSTGRES_DB - name of DB. If not default, also need to change in DB_URL
   * POSTGRES_INITDB_ARGS - using here for locale (needed for correct search in books), if books will be in english use ```POSTGRES_INITDB_ARGS="--locale=en_US"```, and change "russian" to "english" in /app/db/crud -> search_in_book -> query_func + func.ts_headline inside "if results".
   * REDIS_URL - default url to get access to Redis from FastAPI
4. Go to 'infra' dir and start container: ```cd infra/ && docker-compose up -d```
5. Server started! It's available on ```localhost:8000/{endpoint}/```
6. OpenAPI docs are on ```localhost:8000/docs/``` and on ```localhost:8000/redoc/```
7. Add your first book! The easiest way to do it is using redoc. Go to ```localhost:8000/redoc/```, then "Authorize" (use credentials from your .env file), then "Try it out" on "POST /books/", attach your .epub book and "Execute".

## Details
