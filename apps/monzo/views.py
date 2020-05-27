import itertools

from django.forms import models as model_forms
from django.http import JsonResponse
from django.views.generic import (
    DetailView,
    UpdateView,
    MonthArchiveView,
)

from apps.monzo.models import Merchant, Transaction


class SummarisedTransactionsMixin:
    def summarise_transactions(self, transaction_queryset):
        summary = {
            'total_in': 0,
            'total_out': 0,
            'categorised': [],
            'tagged': [],
            'untagged': 0,
        }
        categories = {}
        tagged = {
            'Not tagged': 0,
        }
        subtagged = {}
        summary['declined'] = transaction_queryset.filter(declined=True).count()
        summary_queryset = transaction_queryset.exclude(
            declined=True,
            include_in_spending=True
        )
        for transaction in summary_queryset:
            if transaction.amount < 0:
                amount = (-1 * transaction.amount)
                if transaction.include_in_spending:
                    summary['total_out'] += amount
                    try:
                        categories[transaction.category] += amount
                    except KeyError:
                        categories[transaction.category] = amount

                    tags = transaction.tags()
                    if tags:
                        if len(tags) == 1:
                            tag = tags[0]
                            if tag.name not in tagged:
                                tagged[tag.name] = amount
                            else:
                                tagged[tag.name] += amount
                        else:
                            for tag in tags:
                                if tag.name not in tagged:
                                    tagged[tag.name] = amount
                                else:
                                    tagged[tag.name] += amount
                            for a,b in itertools.permutations(tags, 2):
                                if a.name not in subtagged:
                                    subtagged[a.name] = {}
                                if b.name not in subtagged[a.name]:
                                    subtagged[a.name][b.name] = amount
                                else:
                                    subtagged[a.name][b.name] += amount
                    else:
                        tagged['Not tagged'] += amount
            else:
                summary['total_in'] += transaction.amount

        for category in categories:
            summary['categorised'].append({
                'name': category,
                'total': categories[category]
            })
        summary['tagged'] = []

        # seen = {}
        for tag,total in sorted(tagged.items(), key=lambda x: x[1], reverse=True):
            subtags = []
            if tag in subtagged:
                for subtag in subtagged[tag]:
                    # combo = '%s:%s' % tuple(sorted([tag, subtag]))
                    # if combo not in seen:
                        # seen[combo] = 1
                    subtag_total = subtagged[tag][subtag]
                    if subtag_total != total:
                        subtags.append({
                            'name': subtag,
                            'total': subtag_total,
                        })
            summary['tagged'].append({
                'name': tag,
                'total': total,
                'subtags': subtags,
            })
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


class AjaxResponseMixin:
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.is_ajax():
            return JsonResponse({'ok':True})
        else:
            return response


class SingleFieldUpdateView(AjaxResponseMixin, UpdateView):
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
