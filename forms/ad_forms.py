from django.forms import ModelForm
from django import forms


def override_clean(self):
    """
    重写clean方法,用于自定义验证
    :param self:
    :return:
    """
    # print("cleaned_dtat:", self.cleaned_data)
    # print("validataion errors:",self.errors)
    if self.Meta.admin.readonly_table is True:
        raise forms.ValidationError(("This is a readonly table!"))
    if self.errors:
        raise forms.ValidationError(("Please fix errors before re-submit."))
    if self.instance.id is not None:  # means this is a change form ,should check the readonly fields
        for field in self.Meta.admin.readonly_fields:
            old_field_val = getattr(self.instance, field)
            form_val = self.cleaned_data.get(field)
            # print("filed differ compare:", old_field_val, form_val)
            if old_field_val != form_val:
                if self.Meta.partial_update:  # for list_editable feature
                    if field not in self.cleaned_data:
                        # 因为list_editable成生form时只生成了指定的几个字段，所以如果readonly_field里的字段不在，list_ediatble数据里，那也不检查了
                        continue  #

                self.add_error(field, "Readonly Field: field should be '{value}' ,not '{new_value}' ". \
                               format(**{'value': old_field_val, 'new_value': form_val}))


# django是通过"__new__"方法，找到ModelForm里面的每个字段的
def __new__(cls, *args, **kwargs):
    """
    这里给字段添加样式限制、提示等
    :param cls:
    :param args:
    :param kwargs:
    :return:
    """
    for field_name in cls.base_fields:
        field = cls.base_fields[field_name]
        # print("field info:", field_name, field)  # referral_from <django.forms.models.ModelChoiceField object at 0x000001A87BF47828>
        attr_dic = {'placeholder': field.help_text, 'class': 'form-control'}
        if 'BooleanField' in field.__repr__():
            attr_dic.update({'class': 'custom-control custom-checkbox'})
        if 'TypedChoiceField' in field.__repr__():
            attr_dic.update({'class': 'custom-select d-block w-100'})
        if 'ModelChoiceField' in field.__repr__():  # 外键关联字段
            attr_dic.update({'data-tag': field_name})
        # print("attr_dic:", attr_dic)
        field.widget.attrs.update(attr_dic)

        if hasattr(cls.Meta.model, "clean_%s" % field_name):
            clean_field_func = getattr(cls.Meta.model, "clean_%s" % field_name)
            # print("clean_field_func:", clean_field_func)
            # print("filed name:", field_name)
            setattr(cls, "clean_%s" % field_name, clean_field_func)
    else:
        setattr(cls, "clean", override_clean)
    return ModelForm.__new__(cls)


def init_modelform(model_class, fields, admin_class, **kwargs):
    """
    创建Model Form,不同于以往,这个创建是动态的..以满足不同角色
    :param model_class:
    :param fields:
    :return: ModelForm对象
    """
    # type创建参考备忘
    # new_class = type('Cat', (object,), {'meow': remote_call('meow'), 'eat': remote_call('eat'), 'sleep': remote_call('sleep')})
    class Meta:
        pass
    print("model_class:", model_class)
    setattr(Meta, 'model', model_class)
    print("fields:", fields)
    setattr(Meta, 'fields', fields)
    setattr(Meta, 'admin', admin_class)
    setattr(Meta, 'update_tb', kwargs.get('update_tb'))
    attrs = {'Meta': Meta}

    name = 'DynamicModelForm'
    create_class = (ModelForm, )
    model_form = type(name, create_class, attrs)
    setattr(model_form, '__new__', __new__)
    return model_form
