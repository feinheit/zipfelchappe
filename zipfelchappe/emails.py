from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.template.loader import render_to_string


def render_mail(template, context):
    subject = render_to_string('zipfelchappe/emails/%s_subject.txt' % template,
        context).strip()
    message = render_to_string('zipfelchappe/emails/%s_message.txt' % template,
        context)

    return subject, message


def send_successful_message(project, pledge):
    backer = pledge.backer

    ctx = {
        'project': project,
        'pledge': pledge,
        'backer': backer,
        'site': Site.objects.get_current()
    }

    subject, message = render_mail('project_successful', ctx)

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
        [backer.email], fail_silently=True)


def send_unsuccessful_message(project, pledge):
    backer = pledge.backer

    ctx = {
        'project': project,
        'pledge': pledge,
        'backer': backer,
        'site': Site.objects.get_current()
    }

    subject, message = render_mail('project_unsuccessful', ctx)

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
        [backer.email], fail_silently=True)


def send_pledge_completed_message(pledge, mail_template=None):

    if mail_template is not None:
        context = Context({'pledge': pledge})
        subject = Template(mail_template.subject).render(context)
        message = Template(mail_template.template).render(context)
    else:
        subject, message = render_mail('pledge_completed', {'pledge': pledge})

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
        [pledge.backer.email], fail_silently=False)
