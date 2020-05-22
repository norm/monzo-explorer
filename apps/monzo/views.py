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


class TransactionView(DetailView):
    model = Transaction


class TransactionNoteUpdate(UpdateView):
    model = Transaction
    fields = ['user_note']
    template_name = 'monzo/transaction_note_form.html'


class TransactionTagsUpdate(UpdateView):
    model = Transaction
    fields = ['user_tags']
    template_name = 'monzo/transaction_tags_form.html'


class MerchantView(DetailView):
    model = Merchant


class MerchantTagsUpdate(UpdateView):
    model = Merchant
    fields = ['user_tags']
    template_name = 'monzo/merchant_tags_form.html'

    def get_success_url(self):
        if 'success' in self.request.POST:
            return self.request.POST['success']
        return super().get_success_url()

