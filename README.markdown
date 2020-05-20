monzo-explorer
==============

A django app for me to archive and explore my Monzo transaction data.


Get setup
---------

From a checkout of this repository, create/activate a virtualenv, then
`pip install -r requirements.txt`.

Create a `.env` file, populated with:

    PYTHONUNBUFFERED=1
    SECRET_KEY="__FILL_OUT__"
    DEBUG=1
    DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1"
    DJANGO_PORT=8669

Generate a new secret key with:

    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())

Run the app with `honcho start`.
