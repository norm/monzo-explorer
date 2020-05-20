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
    MONZO_CLIENT_KEY="__FILL_OUT__"
    MONZO_SECRET_KEY="__FILL_OUT__"
    MONZO_REDIRECT_URL="http://localhost:8669/callback"

Generate a new secret key with:

    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())

Create a new OAuth Client in the [Monzo Developer Portal][mdp]. 

The Monzo client and secret keys can be found in your dev portal. Fill out
the name and description, and set the redirect URL to
`http://localhost:8669/callback`. Add the `client ID` and `client secret`
values to the `.env` file.


Authenticate with Monzo
-----------------------

Run the app with `honcho start`, and open `http://localhost:8669` in your
browser. Click "Authenticate with Monzo" if this is the first time using it.
Allow the app to use your data by approving the request in the Monzo app
on your phone.
