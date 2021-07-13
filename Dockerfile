FROM python:3

WORKDIR /usr/app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src src

ENTRYPOINT [ "python", "./src/processHistorian.py" ]