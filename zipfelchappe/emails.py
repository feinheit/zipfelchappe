from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.db.models.signals import class_prepared, post_save
from django.template.loader import render_to_string as render_str

from .models import Project, Update

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

        subject = render_str('zipfelchappe/emails/new_update_subject.txt', ctx).strip()
        content = render_str('zipfelchappe/emails/new_update_content.txt', ctx)

        send_mail(subject, content, 'noreply@feinheit.ch',
            [backer.email], fail_silently=False)

    update.mails_sent = True
    update.save()

post_save.connect(send_update_mail, sender=Update)
