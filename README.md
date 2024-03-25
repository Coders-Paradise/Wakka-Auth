# Wakka Auth

Full featured JWT Authentication Service by supporting multi-tenancy.

## Getting Started

This software aims at providing a secure authentication service to multiple applications under the same hood by harnessing the power of JSON Web Token.

## Installing

### Local System

Wakka Auth has the following dependencies to be met in order to install on local system

#### Dependencies

```
Python >=  3.10
MySQL  >=  8.0
Linux (Preferred)
```

Installing and activating virtualenv

```
pip install virtualenv
virtualenv venv
```

Install requirements

```
cd wakka_auth
pip install -r requirements.txt
```

Follow the `.env.template` file, replace the values and export the environment variables to the terminal

Boot up the MySQL database, if not started yet.

Perform database migrations

```
cd wakka_auth
python manage.py migrate
```

Create Superuser by using the following command and enter all the fields as prompted

```
cd wakka_auth
python manage.py createsuperuser
```

Run the application using

```
cd wakka_auth
python manage.py runserver
```

### In Docker

Build the docker compose

```
docker compose build
```

Run the docker compose

```
docker compose up
```

## Environment variables specifications

- `WAKKA_DEBUG` - boolean value specifying the Django application mode defaults to `false`. Set either `true` and `false`.
- `WAKKA_DB_NAME` - name of database in MySQL
- `WAKKA_DB_USER` - username of the user for MySQL
- `WAKKA_DB_PASS` - password of the user for MySQL
- `WAKKA_DB_HOST` - host of MySQL server
- `WAKKA_DB_PORT` - port of MySQL server
- `WAKKA_SECRET_KEY` - crypographic key for Django's internal security measures
- `WAKKA_JWT_PRIVATE_KEY` - **RSA512** private key of a key pair
- `WAKKA_JWT_PUBLIC_KEY` - **RSA512** public key of a key pair
- `WAKKA_EMAIL_HOST` - host for SMTP server
- `WAKKA_EMAIL_FROM` - from address to be shown in Email
- `WAKKA_EMAIL_HOST_USER` - username for SMTP server authentication, commonly Email is used
- `WAKKA_EMAIL_HOST_PASSWORD` - password of the user for SMTP server
- `WAKKA_SINGLE_APP` - boolean value allowing the application to run only for single app, defaults to `false`. Set either `true` and `false`.
- `WAKKA_APP_NAME` - client app name to be used when single app mode is set to **true**.
- `ADMIN_PORTAL_PATH` - path of management portal for admin

## API Specifications

Run wakka auth in debug mode and access the following endpoints to access the whole API documentation. (Documentation is available only in debug mode)

```
docs/swagger/
docs/redoc/
```

Refer `wakka_auth/wakka/urls.py` for below:

- `user_urlpatterns` will be accessed only by application server
- rest others will be accessed by the client

## Features

- Allows to create and manage users for **multiple** applications in a single point without any conflicts
- **Obtain** the token pair and **refresh** the access token
- **Soft delete** feature to enable history tracking and audit purpose
- Email-based **email verification** and **password reset** functionality

## Flow Diagram

App creation in multi-tenancy mode

```
┌──────────────────────┐
│                      │
│     Create App       │
│                      │
└──────────┬───────────┘
           │
           │
           │
┌──────────▼───────────┐
│                      │
│     Copy API key     │
│                      │
└──────────┬───────────┘
           │
           │
           │
┌──────────▼───────────┐
│                      │
│    Nullify API key   │
│                      │
└──────────┬───────────┘
           │
           │
           │
┌──────────▼───────────┐
│                      │
│   Nullify API key    │
│                      │
└──────────┬───────────┘
           │
           │
           │
┌──────────▼───────────┐
│                      │
│ Use API key in header│
│                      │
└──────────────────────┘
```

User flow in Wakka Auth

```
┌──────────────────────┐
│                      │
│     Create User      │
│                      │
└──────────┬───────────┘
           │
           │
           │
┌──────────▼───────────┐
│                      │
│     Verify email     │
│                      │
└──────────┬───────────┘
           │
           │
           │
┌──────────▼───────────┐
│                      │
│  Obtain token pair   │
│                      │
└──────────┬───────────┘
           │
           │
           │
┌──────────▼───────────┐
│                      │
│  Refresh if expired  │
│                      │
└──────────┬───────────┘
           │
           │
           │
┌──────────▼───────────┐
│                      │
│Reset Password if need│
│                      │
└──────────────────────┘
```

## Security measures

### Key Pair

- `RSA512` public-private key pair is used to secure signing and validation of JWT tokens, where the private key is used by wakka to sign the token whereas public key is used by client and App servers to validate the token securely.

### Validate App name in header

- Each app is allocated with unique `app_name` and access key to authenticate the server in multi-tenant mode.

### Server API key for server-wakka communication

- Respective Applications is allocated with unique API keys, using which they can communicate with Wakka Auth.

## HTTP Headers

The header following header is required in multi-tenant mode, from both client to wakka, and app server to wakka communication

```
X-App-Name: <Your App Name>
```

The following header is always required in each request made by the app server
to wakka

```
X-Server-Api-Key: <Your Secret Api Key>
```

## Key Notes

- Wakka Auth can be used as standalone authentication service for more than one application or can be tailored for single application.
- When deployed in single app mode, the entire management should be taken care by the respective party.

## Built With

- [Python](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [JWT- Json Web Token](https://jwt.io/)
- [PyJWT](https://pypi.org/project/PyJWT/)
- [MySQL](https://www.mysql.com/)

## TODO

- LRU based Token Rotation
- Message queue for asynchronous activities
- Reset Password Functionality
- Meta tag for user (if needed)
