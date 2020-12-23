FROM python:3.9

RUN mkdir /app

WORKDIR /app

RUN pip install pipenv

COPY Pipfile* ./

RUN pipenv install

COPY . .

EXPOSE 5000

ENV FLASK_ENV production

CMD [ "pipenv", "run", "gunicorn", "app:app", "-b", "0.0.0.0:5000" ]
