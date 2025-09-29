FROM python 
WORKDIR /app

RUN pip install "fastapi[standard]" pymongo

COPY . .

EXPOSE 8000

CMD ["fastapi", "dev", "./main.py", "--host", "0.0.0.0"]