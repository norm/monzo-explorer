from datetime import datetime

from dateutil.relativedelta import relativedelta
from monzo import Monzo, MonzoOAuth2Client

from django.db import models
from django.utils.timezone import make_aware
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase


def text_to_timestamp(text):
    try:
        timestamp = make_aware(datetime.strptime(
            text,
            '%Y-%m-%dT%H:%M:%S.%fZ',
        ))
    except ValueError:
        timestamp = make_aware(datetime.strptime(
            text,
            '%Y-%m-%dT%H:%M:%SZ',
        ))
    return timestamp


class Transaction(models.Model):
    id = models.CharField(
        max_length = 64,
        primary_key = True,
    )
    created = models.DateTimeField()
    description = models.CharField(
        max_length = 128,
        null = True,
        blank = True,
    )
    amount = models.IntegerField()
    currency = models.CharField(max_length = 10)
    merchant = models.ForeignKey(
        'Merchant',
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
    )
    notes = models.CharField(
        max_length = 128,
        null = True,
        blank = True,
    )
    category = models.CharField(
        max_length = 64,
        null = True,
        blank = True,
    )
    settled = models.DateTimeField(
        null = True,
        blank = True,
    )
    local_amount = models.IntegerField()
    local_currency = models.CharField(max_length = 10)
    updated = models.DateTimeField(
        null = True,
        blank = True,
    )
    declined = models.BooleanField(default = False)
    decline_reason = models.CharField(
        max_length = 128,
        null = True,
        blank = True,
    )
    card_check = models.BooleanField(default = False)
    scheme = models.CharField(max_length = 64)
    include_in_spending = models.BooleanField(default = True)

    # metadata ...
    # labels (always null)
    # account_balance (always 0)
    # attachments (I don't use this ... yet?)
    # international (always null)
    # categories (just the category with the amount, possibly to allow to break down further later?)
    # is_load (always false?)
    # account_id = models.ForeignKey('Account')
    # user_id = after 2018
    # counterparty ...
    # dedupe_id (used by transactions for safe retries)
    # originator (did I do it)
    # can_be_excluded_from_breakdown (don't care)
    # can_be_made_subscription (don't care)
    # can_split_the_bill (don't care)
    # can_add_to_tab (don't care)
    # amount_is_pending (doesn't seem reliable)
    # atm_fees_detailed (null)

    user_note = models.CharField(
        max_length = 1024,
        null = True,
        blank = True
    )
    user_tags = TaggableManager(
        through = 'TaggedTransaction',
        blank = True
    )

    class Meta:
        ordering = ['-created']

    @classmethod
    def fetch_data_from_monzo(cls, fetch_all=False):
        oauth_client = MonzoOAuth2Client.from_json('monzo.json')
        client = Monzo.from_oauth_session(oauth_client)
        accounts = client.get_accounts()
        since = None

        if not fetch_all:
            since = (
                datetime.now() +
                relativedelta(days=-89, hour=0, minute=0, second=0)
            ).strftime('%Y-%m-%dT%H:%M:%SZ')

        for account in accounts['accounts']:
            print('Account %s: ' % account['id'], end='')
            if not fetch_all and account['closed']:
                print('skipping as closed')
                continue
            transactions = client.get_transactions(
                account['id'],
                since=since,
            )

            total_created = 0
            total_fetched = 0
            for transaction in transactions['transactions']:
                total_fetched += 1
                obj, created = Transaction.update_from_monzo_data(transaction)
                if created:
                    total_created += 1

            print('%s updated, %s new' % (total_fetched, total_created))

    @classmethod
    def update_from_monzo_data(cls, transaction):
        update = {
            'created': text_to_timestamp(transaction['created']),
            'description': transaction['description'],
            'amount': transaction['amount'],
            'currency': transaction['currency'],
            'local_amount': transaction['local_amount'],
            'local_currency': transaction['local_currency'],
            'updated': text_to_timestamp(transaction['updated']),
            'scheme': transaction['scheme'],
            'category': transaction['category'],
            'include_in_spending': transaction['include_in_spending'],
        }

        if transaction['merchant'] is not None:
            update['merchant'], _ = \
                Merchant.update_from_monzo_data(transaction['merchant'])

        if transaction['settled'] != '':
            transaction['settled'] = text_to_timestamp(transaction['settled'])

        try:
            update['decline_reason'] = transaction['decline_reason']
            update['declined'] = True
        except KeyError:
            pass

        if transaction['notes'] == 'Active card check':
            update['card_check'] = True

        return cls.objects.update_or_create(
            id=transaction['id'],
            defaults = update,
        )

    def __str__(self):
        if self.declined:
            declined = 'DECLINED '
        else:
            declined = ''
        return u'%s %s %.2f %s' % (
            self.created.strftime('%Y-%m-%dT%H:%M:%S'),
            declined,
            self.amount / 100,
            self.description,
        )


class TaggedTransaction(TaggedItemBase):
    content_object = models.ForeignKey(
        'Transaction',
        on_delete=models.CASCADE,
    )


class Merchant(models.Model):
    id = models.CharField(
        max_length = 64,
        primary_key = True,
    )
    group_id = models.CharField(max_length=64, null=True, blank=True)
    name = models.CharField(max_length=128)
    logo = models.URLField()
    address = models.CharField(max_length=1024, null=True, blank=True)
    postcode = models.CharField(max_length=16, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    twitter_id = models.CharField(max_length=16, null=True, blank=True)
    foursquare_id = models.CharField(max_length=16, null=True, blank=True)

    @classmethod
    def update_from_monzo_data(cls, merchant):
        details = {
            'group_id': merchant['group_id'],
            'name': merchant['name'],
            'logo': merchant['logo'],
            'address': merchant['address']['formatted'],
            'postcode': merchant['address']['postcode'],
            'latitude': merchant['address']['latitude'],
            'longitude': merchant['address']['longitude'],
        }
        try:
            details['foursquare_id'] = merchant['metadata']['foursquare_id']
        except KeyError:
            pass

        try:
            details['twitter_id'] = merchant['metadata']['twitter_id'].lstrip('@')
        except(AttributeError, KeyError):
            pass

        return cls.objects.update_or_create(
            id = merchant['id'],
            defaults = details,
        )

    def __str__(self):
        return self.name
