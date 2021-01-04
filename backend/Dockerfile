FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt-get update && apt-get -y upgrade && apt -y install graphviz xdg-utils
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=api.py

COPY . .

EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0" ]