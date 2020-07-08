FROM python:3

WORKDIR /usr/src/app

COPY Ativos.csv .
COPY main.py
COPY module.py
COPY test_etl.py
COPY Requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]

