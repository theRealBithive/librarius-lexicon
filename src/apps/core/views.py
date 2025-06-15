from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Audiobook


class AudiobookListView(ListView):
    model = Audiobook
    template_name = 'core/audiobook_list.html'
    context_object_name = 'audiobooks'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_count'] = Audiobook.objects.filter(status='pending').count()
        context['processed_count'] = Audiobook.objects.filter(status='processed').count()
        return context


class AudiobookUpdateView(UpdateView):
    model = Audiobook
    template_name = 'core/audiobook_edit.html'
    fields = ['title', 'author', 'series', 'narrator']
    success_url = reverse_lazy('core:audiobook-list')

    def form_valid(self, form):
        messages.success(self.request, 'Audiobook metadata updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
