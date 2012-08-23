
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
from .app_settings import ALLOW_ANONYMOUS_PLEDGES

class BackProjectForm(forms.ModelForm):

    amount = forms.IntegerField(label=_('amount'),
        widget=forms.widgets.TextInput(attrs={'maxlength':'4'}))

    class Meta:
        model = Pledge
        exclude = ('backer', 'status') if ALLOW_ANONYMOUS_PLEDGES else \
                  ('backer', 'status', 'anonymously')
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
        self.fields['reward'].label = _('reward')
        self.fields['reward'].empty_label = _('No reward')
        self.fields['reward'].label_from_instance = self.label_for_reward

    def label_for_reward(self, reward):
        return render_to_string('zipfelchappe/reward_option.html', {
            'reward': reward,
            'project': self.project
        })

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if amount < 5:
            raise forms.ValidationError(_('Please, just 5 bucks!'))

        if amount > 2000:
            raise forms.ValidationError(_('Sorry, 2000 is the maximal amount'))

        return amount

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

    class Media:
        js = ("zipfelchappe/js/loading_wall.js",)

class RegisterUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        for field in ('first_name', 'last_name', 'email'):
            self.fields[field].required=True

    class Media:
        js = ("zipfelchappe/js/loading_wall.js",)

class RegisterBackerForm(forms.ModelForm):

    class Meta:
        model = get_backer_model()
        exclude = ('user', '_first_name', '_last_name', '_email')

    class Media:
        js = ("zipfelchappe/js/loading_wall.js",)

class UserlessBackerForm(forms.ModelForm):

    class Meta:
        model = get_backer_model()
        exclude = ('user')

    def __init__(self, *args, **kwargs):
        super(UserlessBackerForm, self).__init__(*args, **kwargs)
        for field in ('_first_name', '_last_name', '_email'):
            self.fields[field].required=True

    class Media:
        js = ("zipfelchappe/js/loading_wall.js",)
