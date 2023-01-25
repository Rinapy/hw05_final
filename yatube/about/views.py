from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Выводит статичиску страницу about."""

    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Об авторе'
        return context


class AboutTechView(TemplateView):
    """Выводит статичиску страницу tech."""

    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О технологиях'
        return context