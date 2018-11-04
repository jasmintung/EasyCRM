# 这获得配置的APP,这样不同角色看同一个表时,可以配置

from django import conf


for app in conf.settings.INSTALLED_APPS:
    try:
        print("app:", app)
        app_module = __import__("%s.easy_admin" % app)
        print(app_module.easy_admin.site)
    except ImportError as ex:
        pass
