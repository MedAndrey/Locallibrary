from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime 

class RenewBookForm(forms.Form):
	renewal_date = forms.DateField(help_text="Введите дату между 4 неделями (по умолчанию 3).")


	def clean_renewal_date(self):
		data = self.cleaned_data['renewal_date']

		if data < datetime.date.today():
			raise ValidationError(_('Неверная дата - продление в прошлом'))

		if data > datetime.date.today() + datetime.timedelta(weeks=4):
			raise ValidationError(_('Неверная дата - продление более чем за 4 недели'))

		return data