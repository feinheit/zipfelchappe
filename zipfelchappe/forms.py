
from django import forms
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string

from .models import Project, Pledge, Reward
from .utils import get_backer_model, format_html
from .widgets import BootstrapRadioSelect

class BackProjectForm(forms.ModelForm):

    amount = forms.IntegerField(_('amount'))

    class Meta:
        model = Pledge
        exclude = ('backer', 'status')
        widgets = {
            'project': forms.widgets.HiddenInput,
            'reward': BootstrapRadioSelect,
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')

        initial = kwargs.get('initial', {})
        initial.update({'project': self.project})

        if 'instance' in kwargs:
            initial['amount'] = int(kwargs['instance'].amount)

        kwargs['initial'] = initial

        super(BackProjectForm, self).__init__(*args, **kwargs)

        self.fields['reward'].queryset = self.project.rewards.all()
        self.fields['reward'].empty_label = _('No reward')
        self.fields['reward'].label_from_instance = self.label_for_reward

        #print self.fields['amount'].__dict__

    def label_for_reward(self, reward):
        return render_to_string('zipfelchappe/reward_option.html', {
            'reward': reward
        })

    def clean(self):
        cleaned_data = super(BackProjectForm, self).clean()

        amount = cleaned_data.get('amount')
        reward = cleaned_data.get('reward')

        if reward and amount and reward.minimum > amount:
            raise forms.ValidationError(_('Amount is too small for reward!'))

        if reward and not reward.is_available:
            raise forms.ValidationError(
                _('Sorry, this reward is not available anymore.')
            )

        return cleaned_data

    class Media:
        js = (
            "zipfelchappe/js/loading_wall.js",
            "zipfelchappe/js/project_back_form.js",
        )


class AuthenticatedBackerForm(forms.ModelForm):

    class Meta:
        model = get_backer_model()
        exclude = ('user', '_first_name', '_last_name', '_email')


class RegisterUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        for field in ('first_name', 'last_name', 'email'):
            self.fields[field].required=True


class RegisterBackerForm(forms.ModelForm):

    class Meta:
        model = get_backer_model()
        exclude = ('user', '_first_name', '_last_name', '_email')


class UserlessBackerForm(forms.ModelForm):

    class Meta:
        model = get_backer_model()
        exclude = ('user')

    def __init__(self, *args, **kwargs):
        super(UserlessBackerForm, self).__init__(*args, **kwargs)
        for field in ('_first_name', '_last_name', '_email'):
            self.fields[field].required=True
