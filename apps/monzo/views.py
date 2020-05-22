from django.forms import models as model_forms
from django.views.generic import (
    DetailView,
    UpdateView,
    MonthArchiveView,
)

from apps.monzo.models import Merchant, Transaction


class SummarisedTransactionsMixin:
    def summarise_transactions(self, transactions):
        summary = {
            'total_in': 0,
            'total_out': 0,
            'declined': 0,
            'categorised': {},
            'tagged': {},
            'untagged': 0,
        }
        for transaction in transactions:
            if transaction.declined:
                summary['declined'] += 1
            if transaction.amount < 0:
                if transaction.include_in_spending:
                    summary['total_out'] += (-1 * transaction.amount)
                    try:
                        summary['categorised'][transaction.category] += (-1 * transaction.amount)
                    except KeyError:
                        summary['categorised'][transaction.category] = (-1 * transaction.amount)
                    for tag in transaction.tags():
                        try:
                            summary['tagged'][tag] += (-1 * transaction.amount)
                        except KeyError:
                            summary['tagged'][tag] = (-1 * transaction.amount)
            else:
                summary['total_in'] += transaction.amount

        return summary


class TransactionsMonthView(SummarisedTransactionsMixin, MonthArchiveView):
    model = Transaction
    date_field = "created"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions_summary'] = self.summarise_transactions(
            context['object_list'])
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(
                # FIXME do this properly later (reconcile pot transfers)
                scheme = 'uk_retail_pot'
            ).exclude(
                card_check = True
            )


class SingleFieldUpdateView(UpdateView):
    template_name_suffix = 'update'

    def get_template_names(self):
        return [
            "%s/%s_%s_%s.html" % (
                self.model._meta.app_label,
                self.model._meta.model_name,
                self.field,
                self.template_name_suffix,
            ),
        ]

    def get_form_class(self):
        return model_forms.modelform_factory(self.model, fields=[self.field])

    def get_success_url(self):
        if 'success' in self.request.POST:
            return self.request.POST['success']
        return super().get_success_url()


class TransactionView(DetailView):
    model = Transaction


class TransactionNoteUpdate(SingleFieldUpdateView):
    model = Transaction
    field = 'user_note'


class TransactionTagsUpdate(SingleFieldUpdateView):
    model = Transaction
    field = 'user_tags'


class TransactionReviewedUpdate(SingleFieldUpdateView):
    model = Transaction
    field = 'user_reviewed'


class MerchantView(DetailView):
    model = Merchant


class MerchantTagsUpdate(SingleFieldUpdateView):
    model = Merchant
    field = 'user_tags'
