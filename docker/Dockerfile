FROM python:3

WORKDIR /usr/src/app

COPY Ativos.csv .
COPY main.py .
COPY module.py .
COPY test_etl.py .
COPY requirements.txt .
RUN apt-get update
RUN apt-get install -y locales locales-all
ENV LC_ALL pt_BR.UTF-8
ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR.UTF-8

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]

