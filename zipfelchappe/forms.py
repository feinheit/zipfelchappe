
from django import forms

from .utils import get_backer_model

class BackerForm(forms.ModelForm):

    class Meta:
        model = get_backer_model()
        exclude = ('user',)
