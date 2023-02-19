# Deployment

This guide is for deployment on [Uberspace](https://uberspace.de/).

## Create web backend

```bash
uberspace web backend set /kachel --http --port 63793 --remove-prefix
```

## Run application through supervisord

Create the service file `~/etc/services.d/kachel.ini`:

```ini
[program:kachel]
command=/home/$USER/.cache/pypoetry/virtualenvs/kachel-1vp70cUJ-py3.11/bin/gunicorn --reload --chdir /home/$USER/Projects/kachel/ --bind 0.0.0.0:63793 kachel.wsgi:app
autostart=yes
autorestart=yes
# `startsecs` is set by Uberspace monitoring team, to prevent a broken service from looping
startsecs=30
```

Reread the service via `supervisorctl reread` and start it through `supervisorctl start kachel`.

## Setup cron job

```bash
#!/usr/bin/bash

# Absolute path this script is in
BASEDIR=$(dirname "$0")

pushd $BASEDIR
poetry run python kachel/cache.py download <ENDPOINT>
supervisorctl restart kachel
popd
```

and something like `0 0 * * * /usr/bin/bash /home/$USER/Projects/kachel/cron.sh`
via `crontab -e`.
