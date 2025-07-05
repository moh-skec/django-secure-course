# Secure Coding with Django

Created by Rudolf Olah <rudolf.olah.to@gmail.com>
Modified by Mohammadhossein Shahpoori <shahpoorymohammadhossein@gmail.com>

## Setup Django

Get started with Django:

```sh
# Install redis for background task queues
# On Linux/GitHub Codespaces:
sudo apt-get update
sudo apt-get install redis-server -y
# On Mac OS X:
brew install redis

# Set up the environment and install packages
# For GitHub Codespaces / Linux environments
python3 -m venv env
source env/bin/activate
pip install setuptools  # Required for Django 3.0.6 compatibility with Python 3.12
pip install -r requirements.txt

# Note: If celery installation fails with metadata errors, use:
# pip install "celery[redis]>=5.0" instead of the version in requirements.txt

# Django app
cd demo
# Run model and data migrations
python manage.py migrate

# Create admin user
# python manage.py createsuperuser --username admin

# Run redis server in another terminal:
# For GitHub Codespaces, start with:
sudo service redis-server start
# For local development, use:
redis-server

# Run the background worker in another terminal:
celery -A demo worker -l info

# Run tests
python manage.py test

# Run the server
python manage.py runserver
```

## Users and Data and Logging In

There is some data loaded into the database after you run `python manage.py migrate` and a few users are created.

**Use the username as the password to login**:

- `admin`
- `user_a`
- `user_b`
- `user_c`

You can login with these users through the frontend application `http://localhost:4200` and through the Django admin `http://localhost:8000/admin/`
