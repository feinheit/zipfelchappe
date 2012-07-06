
from django import forms
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import Project, Payment, Reward
from .utils import get_backer_model, format_html
from .widgets import BootstrapRadioSelect


class BackProjectForm(forms.ModelForm):

    amount = forms.IntegerField(_('amount'))

    def label_for_reward(self, reward):
        return format_html(
            u'<div class="radio_text"><strong>{0} {1}: {2}</strong><br/>{3}</div>',
            reward.minimum,
            reward.project.currency,
            reward.title,
            reward.description
        )

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(BackProjectForm, self).__init__(*args, **kwargs)
        self.fields['reward'].queryset = self.project.rewards.all()
        self.fields['reward'].empty_label = _('No reward')
        self.fields['reward'].label_from_instance = self.label_for_reward

    class Meta:
        model = Payment
        exclude = ('backer',)
        widgets = {
            'project': forms.widgets.HiddenInput,
            'reward': BootstrapRadioSelect,
        }
