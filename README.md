# Code Reviewers (BACKEND)

A website for developers to upload and review code. [Check it out](https://codereviewers.gq)!  
This is the backend. For the frontend, click [here](https://github.com/arnu515/code-reviewers)

## Quickstart

You will need a DigitalOcean Spaces Space with an API Key configured. This will be used to store the code that users submit. Add these environment variables:
```
SPACES_ACCESS_KEY=accesskey
SPACES_SECRET_KEY=secretkey
SPACES_SPACE_REGION=region
SPACES_SPACE_NAME=bucketname
FLASK_ENV=production
```

Additionally, also set some fernet keys (obtainable with this command):
```sh
python3 -c "from cryptograhpy.fernet import Fernet; print(Fernet.generate_key().decode())"
```
and generate 3 keys and put them as environment variables like so:
```
FERNET_KEY_1=key
FERNET_KEY_2=key
FERNET_KEY_3=key
```

### Deploy with DigitalOcean

[![Deploy to DO](https://mp-assets1.sfo2.digitaloceanspaces.com/deploy-to-do/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/arnu515/code-reviewers-backend/tree/master)

You will also need a Redis and PostgreSQL Database, which is available on DigitalOcean. Create a DigitalOcean Database and add it to your app as a component. Then, create an environment variable called `REDIS_URL` and set it to the connection string of your database. Format of a connection string should be:

```
redis://user:password@url:port/databasenumber
```

Do the same with `SQLALCHEMY_DATABASE_URL` environment variable, which is the same thing as `REDIS_URL`, but for postgres.

### Manually deploy

Set your environment variables:
```
REDIS_URL=url_of_the_redis_instance
SQLALCHEMY_DATABASE_URL=url_of_your_database
```

#### Deploy with docker

To make deployment easier, there's Docker support. Make sure that `docker` and `docker-compose` are installed on your system.

```sh
$ docker --version
Docker version XX.XX.X, build XXXXXXX
$ docker-compose --version
docker-compose version X.XX.X, build XXXXXXXX
```

Then, use `docker-compose` to run the app.

```sh
$ git clone https://github.com/arnu515/code-reviewers.git code-reviewers
$ cd code-reviewers
$ docker-compose up
```

> You can also use the normal Dockerfile, but you'll need a redis and postgres instance available to you

Visit the app at [localhost:3000](http://localhost:3000)

#### "Traditional" method

> You will need to have redis, postgres and python3 with pip3 installed for this.

0. Install pipenv if you don't have it already
```
$ pip3 install pipenv
```

1. Clone the repo
```
$ git clone https://github.com/arnu515/code-reviewers.git code-reviewers
$ cd code-reviewers
```

2. Install dependencies
```
$ pipenv install
```

3. Build and run the app
```
# production
$ pipenv run gunicorn app:app -b 0.0.0.0:5000
# development
$ flask run
```

4. Visit your app at [localhost:5000](http://localhost:5000)
