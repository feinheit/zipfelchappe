from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.db.models.signals import class_prepared, post_save
from django.template.loader import render_to_string

from .models import Project, Update

def render_mail(template, context):
    subject = render_to_string('zipfelchappe/emails/%s_subject.txt' % template,
        context).strip()
    message = render_to_string('zipfelchappe/emails/%s_message.txt' % template,
        context)

    return subject, message


def send_update_mail(sender, instance, **kwargs):
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

        send_mail(subject, message, 'noreply@feinheit.ch',
            [backer.email], fail_silently=False)

    update.mails_sent = True
    update.save()

post_save.connect(send_update_mail, sender=Update)


def send_successfull_message(project, pledge):

    backer = pledge.backer

    ctx = {
        'project': project,
        'pledge': pledge,
        'backer': backer,
        'site': Site.objects.get_current()
    }

    subject, message = render_mail('project_successfull', ctx)

    send_mail(subject, message, 'noreply@feinheit.ch',
        [backer.email], fail_silently=False)


def send_unsuccessfull_message(project, pledge):

    backer = pledge.backer

    ctx = {
        'project': project,
        'pledge': pledge,
        'backer': backer,
        'site': Site.objects.get_current()
    }

    subject, message = render_mail('project_unsuccessfull', ctx)

    send_mail(subject, message, 'noreply@feinheit.ch',
        [backer.email], fail_silently=False)
