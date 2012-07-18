from django import forms
from django.utils.html import escape, conditional_escape
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import AdminFileWidget

from feincms.templatetags.feincms_thumbnail import cropscale

class AdminImageWidget(AdminFileWidget):

    initial_text = ''
    input_text = _('Change')
    clear_checkbox_label = _('Delete')

    template_with_initial = u'<div style="float:left"> %(initial_text)s %(initial)s %(clear_template)s <br/> %(input_text)s: %(input)s</div>'

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'
        substitutions['input'] = super(forms.ClearableFileInput, self).render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = u'<img src="%s" />' % cropscale(value, '150x150')
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = forms.CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)


class BootstrapRadioFieldRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'<div class="radios">\n%s\n</div>' %
                          u'\n'.join([force_unicode(w) for w in self]))


class BootstrapRadioSelect(forms.RadioSelect):
    renderer = BootstrapRadioFieldRenderer
