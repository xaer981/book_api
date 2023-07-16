# 📚 Book API
This project allow to add .epub books (they will be handled and added to DB (book name, author name, names and texts of chapters)), search in book with query, returning cutted fragment of found text.

## Quick overview
Project using:
* ![Static Badge](https://img.shields.io/badge/FastAPI-green)
* ![Static Badge](https://img.shields.io/badge/Pydantic-green)
* ![Static Badge](https://img.shields.io/badge/SQLAlchemy-green)
* ![Static Badge](https://img.shields.io/badge/PostgreSQL-green)
* ![Static Badge](https://img.shields.io/badge/Docker-green)
* ![Static Badge](https://img.shields.io/badge/Redis-green) ![Static Badge](https://img.shields.io/badge/%2B-orange)
 ![Static Badge](https://img.shields.io/badge/FastAPI_cache-blue?link=https%3A%2F%2Fgithub.com%2Flong2ice%2Ffastapi-cache) ![Static Badge](https://img.shields.io/badge/by-orange)
 [@long2ice](https://github.com/long2ice)
* ![Static Badge](https://img.shields.io/badge/FastAPI_pagination-blue?link=https%3A%2F%2Fgithub.com%2Furiyyo%2Ffastapi-pagination) ![Static Badge](https://img.shields.io/badge/by-orange)
 [@uriyyo](https://github.com/uriyyo)
* ![Static Badge](https://img.shields.io/badge/ebooklib-blue?link=https%3A%2F%2Fgithub.com%2Faerkalov%2Febooklib) ![Static Badge](https://img.shields.io/badge/by-orange)
 [@aerkalov](https://github.com/aerkalov)

## Installation guide
1. Clone current repo: ```git clone https://github.com/xaer981/book_api.git```
2. Go to the new dir and create .env file from example: ```cd book_api/ && cp default.env .env```
   * ADMIN_USER - username for using in HTTP Basic auth to add new books to DB
   * ADMIN_PASSWORD - password for using in HTTP Basic auth to add new books to DB
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


## Usage
1. ### Adding book via ```localhost:8000/docs/```.
   * **Click "Authorize"**
     ![image](https://github.com/xaer981/book_api/assets/99489753/ebe23266-76c8-4be3-93f8-fc14ab02a725)
   * **Use credentials from your .env file and "Authorize" again**
     ![image](https://github.com/xaer981/book_api/assets/99489753/9f6c8fe2-7ff3-4f44-abd9-3582bd769678)
   * **Click "Try it out" in "POST /books/"**
     ![image](https://github.com/xaer981/book_api/assets/99489753/b00d39ef-d054-4a8d-9b01-da466e4c31e5)
   * **Choose your .epub file and "Execute"**
     ![image](https://github.com/xaer981/book_api/assets/99489753/7116f6c2-874d-404c-b125-49f99cb5c733)
   * **Success! You just added a new book.**
     ![image](https://github.com/xaer981/book_api/assets/99489753/7263810c-8945-4db0-824e-59e688867f69)

2. ### Enpoints.
   * **Get all books -> ```GET /books/```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/9c555fc8-f720-4521-9033-6fcd530ee82b)
   * **Get books with pagination -> ```GET /books/?size={desired size}&page={desired page}```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/77f32fac-33e3-4e91-b740-77d88252665f)
   * **Get chapters of book -> ```GET /books/{book_id}/```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/7c1df11e-935c-43ee-826c-6cfaa72a4973)
   * **Get text of chapter -> ```GET /books/{book_id}/chapter/{chapter_number}/```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/3e8159ad-7451-49bc-b60e-7a4193cb3883)
   * **Search chapters in book containing query -> ```GET /books/{book_id}/search/``` + ```body = {"query": "your query"}```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/177f08d7-c717-472a-be46-3d3d3da5876b)
   * **Get all authors -> ```GET /authors/```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/29d0e66f-4849-44c5-80bd-47dfb7b83840)
   * **Get authors with pagination -> ```GET /authors/?size={desired size}&page={desired page}```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/23fdde54-fa83-48ce-b9e9-888b8b52cfda)
   * **Get books of author -> ```GET /authors/{author_id}/```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/2114473f-6a44-4cde-9cb8-c71b9caa6812)


## Technical details
1. ### About credentials.
   * If you're using something without auto encoding of credentials, you should get credentials encoded in base64 to use in HTTP Basic auth.
   * To get encoded credentials, you can use "encode_bs64.py" from "core". Just add ADMIN_USER and ADMIN_PASSWORD in .env (described above) and run this file ```python app/core/encode_bs64.py``` (also need to install dotenv ```python -m pip install python-dotenv``` or use "encode_credentials" function separately.
   * Add header "Authorization" with value ```Basic {your encoded in base64 credentials}```.

2. ### About cache.
   * Project using custom cache key builder (needed to cache paginated results correctly) -> app/core/cache.py "custom_key_builder". If you're not going to use pagination, just delete "key_builder=..." from app/main.py -> "lifespan" function -> FastAPICache.init.
   * Project also using custom cache coder (needed to cache results made with pydantic models ORM correctly).
   * Lifetime. I think that permanent cache meets the requirements of this project. Redis cache flushing on FastAPI shutdown and after adding every new book in DB. If you want to use cache with expire time, just add ```expire={time in seconds}``` to every "cache()" decorator in app/main.py.

3. ### About pagination.
   * Pagination turned on in two endpoints: ```GET /authors/``` and ```GET /books/```. If you want to turn it off, change ```response_model=CustomPage[AuthorInfo]``` in app/main.py -> "author_list" function -> "@app.get" decorator to ```response_model=AuthorInfo```. Same with app/main.py -> "book_list" function -> "@app.get" decorator.

## Finally

If you have any troubles or just want to improve something, feel free to open issues or PRs.

Do not hesitate to contact me 👉 [Telegram](https://t.me/xaer981) 👈

<p align=center>
  <a href="url"><img src="https://github.com/xaer981/xaer981/blob/main/main_cat.gif" align="center" height="40" width="128"></a>
</p>
