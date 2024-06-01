from django import forms
from apps.home.models import *
class AttendanceForm(forms.Form):
    emp_id = forms.ModelChoiceField(queryset=registration.objects.all())
    def __init__(self, *args, **kwargs):
        unknown_row = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if unknown_row:
            self.fields['emp_id'].initial = unknown_row.emp_id