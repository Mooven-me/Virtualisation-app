FROM python 
WORKDIR /app

RUN pip install "fastapi[standard]" sqlmodel pymysql cryptography

COPY . .

CMD ["fastapi", "dev", "./main.py", "--host", "0.0.0.0"]