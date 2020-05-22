from django.views.generic import MonthArchiveView

from apps.monzo.models import Transaction


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
