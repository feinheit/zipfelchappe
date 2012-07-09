
from django import forms
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import Project, Pledge, Reward
from .utils import get_backer_model, format_html
from .widgets import BootstrapRadioSelect


class BackProjectForm(forms.ModelForm):

    amount = forms.IntegerField(_('amount'))

    class Meta:
        model = Pledge
        exclude = ('backer',)
        widgets = {
            'project': forms.widgets.HiddenInput,
            'reward': BootstrapRadioSelect,
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')

        initial = kwargs.get('initial', {})
        initial.update({'project': self.project})
        kwargs['initial'] = initial

        super(BackProjectForm, self).__init__(*args, **kwargs)

        self.fields['reward'].queryset = self.project.rewards.all()
        self.fields['reward'].empty_label = _('No reward')
        self.fields['reward'].label_from_instance = self.label_for_reward

    def label_for_reward(self, reward):
        return format_html(
            u'<div class="radio_text" data-minimum="{0}"><strong>{0} {1}: {2}</strong><br/>{3}</div>',
            reward.minimum,
            reward.project.currency,
            reward.title,
            reward.description
        )

    def clean(self):
        cleaned_data = super(BackProjectForm, self).clean()

        amount = cleaned_data.get('amount')
        reward = cleaned_data.get('reward')

        if reward and reward.minimum > amount:
            raise forms.ValidationError(_('amount is too small for reward!'))

        return cleaned_data

    class Media:
        js = ("zipfelchappe/js/project_back_form.js",)
