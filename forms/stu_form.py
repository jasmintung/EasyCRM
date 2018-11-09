from django.forms import ModelForm
from django import forms
from repository import models


class CustomerForm(ModelForm):
    class Meta:
        model = models.Customer
        exclude = ['customer_note', 'referral_from', 'status', 'sex', 'company', 'salary',
                   'work_status', 'class_type_choices', 'course']
        readonly_fields = ['qq', 'consultant', 'source', 'course', 'class_type']

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)

        for field_name in self.base_fields:
            field = self.base_fields[field_name]
            field.widget.attrs.update({'class': 'form-control'})
            if field_name in CustomerForm.Meta.readonly_fields:
                field.widget.attrs.update({'disabled': 'disabled'})
                self.fields[field_name].required = False  # 不需要检查

    def clean_qq(self):
        print(self.instance.qq)
        if self.cleaned_data.get('qq', None):
            if self.instance.qq != self.cleaned_data['qq']:
                self.add_error('qq', "请不要非法修改!")

    def clean_source(self):
        print(self.cleaned_data['source'])
