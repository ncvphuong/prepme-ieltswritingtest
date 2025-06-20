"""
Core views for the IELTS Writing Test platform.
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(TemplateView):
    """Homepage view."""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'features': [
                {
                    'icon': 'bi-robot',
                    'title': 'AI-Powered Feedback',
                    'description': 'Get detailed feedback on your writing from advanced AI technology.'
                },
                {
                    'icon': 'bi-graph-up',
                    'title': 'Track Progress',
                    'description': 'Monitor your improvement with comprehensive analytics and insights.'
                },
                {
                    'icon': 'bi-collection',
                    'title': '600+ Practice Tasks',
                    'description': 'Access a vast library of IELTS writing tasks for both Academic and General Training.'
                },
                {
                    'icon': 'bi-clock',
                    'title': 'Timed Practice',
                    'description': 'Practice under realistic test conditions with our built-in timer.'
                },
                {
                    'icon': 'bi-award',
                    'title': 'IELTS Band Scoring',
                    'description': 'Receive accurate band scores based on official IELTS criteria.'
                },
                {
                    'icon': 'bi-person-check',
                    'title': 'Personalized Learning',
                    'description': 'Get customized recommendations based on your performance and goals.'
                }
            ]
        })
        return context


class AboutView(TemplateView):
    """About page view."""
    template_name = 'core/about.html'


class HelpCenterView(TemplateView):
    """Help Center page view."""
    template_name = 'core/help.html'


class ContactUsView(TemplateView):
    """Contact Us page view."""
    template_name = 'core/contact.html'


class PrivacyPolicyView(TemplateView):
    """Privacy Policy page view."""
    template_name = 'core/privacy.html'


class TermsOfServiceView(TemplateView):
    """Terms of Service page view."""
    template_name = 'core/terms.html'
