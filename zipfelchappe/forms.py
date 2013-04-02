
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from .models import Pledge
from .widgets import BootstrapRadioSelect
from .app_settings import ALLOW_ANONYMOUS_PLEDGES, PAYMENT_PROVIDERS


class RewardChoiceIterator(forms.models.ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield (u'none', self.field.empty_label)
        if self.field.cache_choices:
            if self.field.choice_cache is None:
                self.field.choice_cache = [
                    self.choice(obj) for obj in self.queryset.all()
                ]
            for choice in self.field.choice_cache:
                yield choice
        else:
            for obj in self.queryset.all():
                yield self.choice(obj)


class RewardChoiceField(forms.models.ModelChoiceField):
    """ Nullable but required ModelChoiceField """
    def _get_choices(self):
        return RewardChoiceIterator(self)

    def to_python(self, value):
        if value == u'none':
            return None
        elif value in EMPTY_VALUES:
            raise ValidationError(_('Please select a reward'))
        try:
            key = self.to_field_name or 'pk'
            value = self.queryset.get(**{key: value})
        except (ValueError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice'])
        return value

    choices = property(_get_choices, forms.fields.ChoiceField._set_choices)


class BackProjectForm(forms.ModelForm):
    """
        The form to create a pledge for a project. It's main tasks are:

        1. Check mount to be positive and higher than zero
        2. Limit amount to 2000 whatevers (no currency based limit)
        3. Limit awards selection to project awards
        4. Only allow adequate awards (minimal amount, still available)
        5. Select payment provider if necessary
    """

    amount = forms.IntegerField(label=_('amount'),
        widget=forms.widgets.TextInput(attrs={'maxlength': '4'}))

    reward = RewardChoiceField(None, widget=BootstrapRadioSelect,
        label=_('reward'), empty_label=_('No reward'), required=False)

    class Meta:
        model = Pledge
        exclude = ('backer', 'status') if ALLOW_ANONYMOUS_PLEDGES else \
                  ('backer', 'status', 'anonymously')
        widgets = {
            'project': forms.widgets.HiddenInput,
            'provider': BootstrapRadioSelect
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')

        initial = kwargs.get('initial', {})
        initial.update({
            'project': self.project,
            'reward': None
        })

        if 'instance' in kwargs:
            initial['amount'] = int(kwargs['instance'].amount)
            initial['reward'] = kwargs['instance'].reward

        kwargs['initial'] = initial

        super(BackProjectForm, self).__init__(*args, **kwargs)

        self.fields['reward'].queryset = self.project.rewards.all()
        self.fields['reward'].label_from_instance = self.label_for_reward

        if len(PAYMENT_PROVIDERS) <= 1:
            del self.fields['provider']
        else:
            self.fields['provider'].choices = PAYMENT_PROVIDERS

    def label_for_reward(self, reward):
        return render_to_string('zipfelchappe/reward_option.html', {
            'reward': reward,
            'project': self.project
        })

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if amount <= 0:
            raise forms.ValidationError(_('Amount must be higher than 0'))

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


class RegisterUserForm(UserCreationForm):
    """ Very simple registration form without double opt-in """

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['email'].required = True

    class Media:
        js = ("zipfelchappe/js/loading_wall.js",)
