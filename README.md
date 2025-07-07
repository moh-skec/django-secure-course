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

# Set up environment variables for development
# Copy the example environment file and update as needed
cp .env.example .env
# Edit .env with your preferred editor and set a secure secret key for production

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

## Security Configuration

This project uses environment variables for sensitive configuration. Make sure to:

1. **Never commit sensitive data** like secret keys, passwords, or API tokens to version control
2. **Use environment variables** for all sensitive configuration (see `.env.example`)
3. **Generate a new secret key** for production deployments
4. **Set `DEBUG=False`** in production
5. **Configure proper `ALLOWED_HOSTS`** for your production domain

### Environment Variables

Required environment variables:

- `DJANGO_SECRET_KEY`: Django secret key (generate a new one for production)
- `DJANGO_DEBUG`: Set to `false` for production
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts for production

Example production settings:

```bash
DJANGO_SECRET_KEY=your-production-secret-key-here
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```
