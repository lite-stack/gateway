# Gateway for Openstack

## To run a local environment

This template can be run it on your local machine. In order to do that you need:

- docker and docker-compose
  https://docs.docker.com/get-docker/
- python 3.10 or higher
  https://www.python.org/downloads/
- venv
  https://linuxhint.com/activate-virtualenv-windows/

## HowTo

1. Clone this repo

  ```console
  git clone <this repo link>
 ```

2. Create <b><i>.env</i></b> file with the environment variables in the project root

  ```dosini
DB_ENGINE=postgres
DB_PORT=5432

DB_HOST=localhost
DB_SCHEMA=openstack
DB_USER=postgres
DB_PASSWORD=postgres

SECRET_KEY=authkey

CLOUD_NAME=local

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=<your email client>
MAIL_PASSWORD=<your password>
MAIL_FROM=info@litestack.com
MAIL_FROM_NAME=LiteStack

MAX_SERVER_LIMIT=15
```

3. Upgrade your pip manager

  ```console
  pip install --upgrade pip
  ```

4. Create and activate a <b><i>virtual environment</i></b> with python virtualenv
   For MacOS/Linux:

  ```console
  pip install virtualenv
  python -m venv venv
  source venv/bin/activate
  ```

For Windows:

  ```console
  pip install virtualenv
  virtualenv venv
  venv\Scripts\activate
  ```

5. Run Postgres inside a docker container

 ```console
 docker-compose -f docker-compose.dev.yml up -d db
 ```

6. Install Alembic (a tool for migrations for the database) and apply migrations.

```console
pip install alembic
alembic upgrade head
```

7. Install the requirments

 ```console
pip install -r requirements.txt
```

8. Run the application

```console
python run.py
```

9. Now the apllication, database and database admin panel must be runned.

- The FastAPI app now is running on [http://localhost:8001](http://localhost:8001)
  To check if everything is correct, open your browser
  at <a href="http://127.0.0.1:8000/" class="external-link" target="_blank"> http://localhost:8000/</a>. You will see
  the JSON response as:

```JSON
{
  "staus": "ok"
}
```

Also you can check auto-generated docs by FastAPI by going
to [http://localhost:8000/docs](http://localhost:8000/docs "http://localhost:8000/docs") or

- PostgreSQL database on localhost:5432

10. To add new table to database or for any other manipulations with the db, you should use migrations. This will allow
    other participants to set up the same db as you.
    Whatch [that video](https://www.youtube.com/watch?v=hO7b4yh-Qfs&list=PLeLN0qH0-mCVQKZ8-W1LhxDcVlWtTALCS&index=5&pp=iAQB "that video")
    to uderstand how to deal with Alembic. After adding a new model to `/app/models`, you need to run:

```console
 alembic revision --autogenerate -m '<name_for_migration>'
```

A new file must be added to `migrations/versions`. To apply the migration run:

```console
alembic upgrade head
```

11. **SKIP THIS POINT FOR NOW** Also you should install pre-commit tool, it will run linter (a tool to not allow to push
    bad pratices/etc. to the repository) and test every time before the commit automatically. So you must make all
    unit-tests valid and keep the project in a good state. To setup pre-commit run:

 ```console
pre-commit
pre-commit autoupdate
  ```

To run precommit manually:

```console
pre-commit run --all-files
```

## Project structure

```
gateway
├── app
│   ├── auth # for fast-api-users library
│   │   ├── config.py # configs for fast
│   │   ├── manager.py
│   │   ├── models.py  # db models
│   │   ├── schemas.py  # pydantic models
│   ├── openstack # will be implemented in future
│   │   ├── client.py  # client model for communication with openstack
│   ├── config.py  # global configs
│   ├── database.py  # db connection related stuff
│   ├── dependencies.py  # db connection related stuff
│   └── main.py
├── logs/ # logs related stuff
├── migrations/ # alembic migrations stuff
│   ├── versions # different versions
├── tests/
│   ├── mocks.py # mocks
│   └── test_main.py # test common functions
├── .env # must be added by you!
├── config.py # globla config for running, all custom configs must be added here.
├── run.py # application runner
├── requirements.txt
```

When you will implement your module, all your stuff must be added to your own folder to `app/<module_name>`. Do not
touch modules of other participants!

## Useful links

1. [Fast API course](https://www.youtube.com/playlist?list=PLeLN0qH0-mCVQKZ8-W1LhxDcVlWtTALCS " Fast API course") **SEE
   FULL!**
2. [Fast API docs](https://fastapi.tiangolo.com/)
3. [Fast API Users docs](https://fastapi-users.github.io/fastapi-users/12.1/)

## DevStack

You need to install DevStack locally to be available to develop the modules.
Install [VM Virtual box](https://www.virtualbox.org/wiki/Downloads), set up
the [Ubuntu server machine](https://releases.ubuntu.com/22.04/) (download **Server install image**) and install all
required stuff for DevStack. Use these links for more information:

1. [DevStack setup article](https://medium.com/@ollste/openstack-local-development-how-to-install-test-and-use-openstack-in-virtualbox-b60b667886c4)
2. [Video with DevStack setup](https://www.youtube.com/watch?v=gAH8jiW8j74)

### Tips

1. While creating `local.conf` file, add this to the file:

```console
[[local|localrc]]
ADMIN_PASSWORD=openstack
DATABASE_PASSWORD=openstack
RABBIT_PASSWORD=openstack
SERVICE_PASSWORD=openstack
HOST_IP=<192.168.56.XXX>
SERVICE_TIMEOUT=180
```

2. Instead of `<192.168.56.XXX> ` at the file `local.conf` add your IP address. To do that, write in the VM `ip addr`,
   find and use your ip with the prefix of `192.168.56.`.
3. Name all users and set all passwords as `openstack`.
4. Update `clouds.yml` file with your IP address, start the app and try to call `/servers/list` from the doc.