from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template import Context, Template
from django.template.loader import render_to_string

from .models import MailTemplate


def render_mail(template, context):
    """ helper to load subject and content from template """
    subject = render_to_string('zipfelchappe/emails/%s_subject.txt' % template,
        context).strip()
    message = render_to_string('zipfelchappe/emails/%s_message.txt' % template,
        context)

    return subject, message


def send_pledge_completed_message(request, pledge, mail_template=None):
    """ Send message after backer successfully pledged to a project """

    # Try to get template from project if not explictly passed
    if mail_template is None:
        try:
            mail_template = MailTemplate.objects.get(
                project=pledge.project,
                action=MailTemplate.ACTION_THANKYOU
            ).translated
        except MailTemplate.DoesNotExist:
            pass

    context = Context({'pledge': pledge, 'user': request.user,
                       'site': get_current_site(request)})
    if mail_template is not None:
        subject = Template(mail_template.subject).render(context)
        message = Template(mail_template.template).render(context)
    else:
        subject, message = render_mail('pledge_completed', context)

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
              [pledge.backer.email], fail_silently=True)
