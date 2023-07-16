# 📚 Book API
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
     ![image](https://github.com/xaer981/book_api/assets/99489753/cdac8e85-0715-4304-92c7-8558c058a8eb)
   * **Use credentials from your .env file and "Authorize" again**
     ![image](https://github.com/xaer981/book_api/assets/99489753/476dfd21-3d6a-4514-840d-14093b559428)
   * **Click "Try it out" in "POST /books/"**
     ![image](https://github.com/xaer981/book_api/assets/99489753/6f2dc25f-2197-4d7b-8594-4d3f0ef4976c)
   * **Choose your .epub file and "Execute"**
     ![image](https://github.com/xaer981/book_api/assets/99489753/c00d43fd-dc8f-49a5-a23e-1f9b5dcccf48)
   * **Success! You just added a new book.**
     ![image](https://github.com/xaer981/book_api/assets/99489753/c8e4e1f9-85b7-4ef2-9084-4ce9476c817d)

2. ### Enpoints.
   * **Get all books -> ```GET /books/```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/747f18de-cb0f-4a7d-9766-6d7fa0f5dc0c)
   * **Get books with pagination -> ```GET /books/?size={desired size}&page={desired page}```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/36747bab-8f22-4c05-a76f-8d23f9351e35)
   * **Get chapters of book -> ```GET /books/{book_id}/```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/ed7c5f06-9803-456d-b09f-7f67b0b86bd6)
   * **Get text of chapter -> ```GET /books/{book_id}/chapter/{chapter_number}/```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/dae99659-c0f7-4bb8-a485-2f49998770d7)
   * **Search chapters in book containing query -> ```GET /books/{book_id}/search/``` + ```body = {"query": "your query"}```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/1111831a-db76-4d72-8b89-2956f349d86c)
   * **Get all authors -> ```GET /authors/```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/529ec5bb-5803-4b66-9bf6-0395498efa64)
   * **Get authors with pagination -> ```GET /authors/?size={desired size}&page={desired page}```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/5d1370ab-74e3-448b-8827-729d529e0053)
   * **Get books of author -> ```GET /authors/{author_id}/```**
     ![image](https://github.com/xaer981/book_api/assets/99489753/9e4b5ba4-2001-4df4-830f-dacfb9d8c405)


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
