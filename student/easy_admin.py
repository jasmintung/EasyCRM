from easycrmadmin.easycrm_admin import BaseEasyCrmAdmin, site
from django.shortcuts import HttpResponse
from student import models


class StuAccountAdmin(BaseEasyCrmAdmin):
    list_display = ('account', 'profile')


site.register(models.Account, StuAccountAdmin)
