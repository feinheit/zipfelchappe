from __future__ import unicode_literals, absolute_import

from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from smtplib import SMTPException

from .models import Project, Backer, Pledge, MailTemplate
from .emails import send_pledge_completed_message

try:
    from django.http import JsonResponse  # Django >= 1.7
except ImportError:
    from django.http import HttpResponse
    import json

    class JsonResponse(HttpResponse):
        def __init__(self, data, *args, **kwargs):
            kwargs['content_type'] = 'application/json'
            super(JsonResponse, self).__init__(
                json.dumps(data), *args, **kwargs)


@csrf_exempt
@staff_member_required
def send_test_mail(request):
    """ Used in the admin to test mail templates """
    project = get_object_or_404(Project, pk=request.POST.get('project', -1))

    action = request.POST.get('action', None)
    subject = request.POST.get('subject', None)
    template = request.POST.get('template', None)
    recipient = request.POST.get('recipient', None)

    mail_template = MailTemplate(
        project=project,
        action=action,
        subject=subject,
        template=template
    )

    fake_plede = Pledge(
        project=project,
        amount=10,
        backer=Backer(
            _first_name=request.user.first_name,
            _last_name=request.user.last_name,
            _email=recipient
        )
    )

    try:
        send_pledge_completed_message(fake_plede, mail_template)
        success = True
    except SMTPException:
        success = False

    return JsonResponse({'success': success})


# Admin views to collect pledges manually

@staff_member_required
def collect_pledges(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    return render(request,
        'admin/feincms/zipfelchappe/project/collect_pledges.html', {
            'project': project,
            'pledges': project.authorized_pledges,
        }
    )


@staff_member_required
def authorized_pledges(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    pledges = []
    for pledge in project.collectable_pledges.all():
        pledges.append({
            'id': pledge.id,
            'amount': pledge.amount_display,
            'backer': pledge.backer.full_name,
            'provider': pledge.provider.capitalize(),
        })

    return JsonResponse(pledges)


@staff_member_required
def collect_pledge(request, project_id, pledge_id):
    pledge = get_object_or_404(Pledge, pk=pledge_id)

    if pledge.provider == 'paypal':
        from .paypal.tasks import process_pledge, PaypalException
        try:
            pp_data = process_pledge(pledge)
            return JsonResponse(pp_data)
        except PaypalException as e:
            return JsonResponse({'error': e.message}, status=400)
    elif pledge.provider == 'postfinance':
        from .postfinance.tasks import (process_pledge,
            PostfinanceException)
        try:
            pf_data = process_pledge(pledge)
            return JsonResponse(pf_data)
        except PostfinanceException as e:
            return JsonResponse({'error': e.message}, status=400)
