from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.db.models.signals import class_prepared, post_save
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from .models import Project, Update

def render_mail(template, context):
    subject = render_to_string('zipfelchappe/emails/%s_subject.txt' % template,
        context).strip()
    message = render_to_string('zipfelchappe/emails/%s_message.txt' % template,
        context)

    return subject, message


def send_update_mail(sender, instance, **kwargs):
    # XXX why not instance.project?
    update = instance
    project = Project.objects.get(pk=update.project.pk)

    if update.status == 'draft' or update.mails_sent:
        return

    for pledge in project.authorized_pledges.all():
        backer = pledge.backer

        ctx = {
            'update': update,
            'project': project,
            'backer': backer,
            'site': Site.objects.get_current()
        }

        subject, message = render_mail('new_update', ctx)

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
            [backer.email], fail_silently=True)

    update.mails_sent = True
    update.save()

post_save.connect(send_update_mail, sender=Update)

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

def send_pledge_completed_message(pledge):

    subject_template = 'zipfelchappe/emails/pledge_completed_subject.txt'
    subject = render_to_string(subject_template).strip()

    templates = [
        'zipfelchappe/emails/pledge_completed_%d.txt' % pledge.project.pk,
        'zipfelchappe/emails/pledge_completed.txt'
    ]

    if pledge.reward:
        templates.insert(0, 'zipfelchappe/emails/pledge_completed_%d_%d.txt' %
                (pledge.project.pk, pledge.reward.pk))

    message = render_to_string(templates, {'pledge': pledge})

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
        [pledge.backer.email], fail_silently=False)
