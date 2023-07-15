FROM python:3.11.1-slim
WORKDIR /book_api
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./app /book_api/app
RUN mkdir -p /book_api/book
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]