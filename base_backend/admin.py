def register_app_models(app_name: str) -> None:
    """
    registers all models of a django app
    should be called in the app's admin module.
    :param app_name: the django app name
    :return: None
    """
    from django.contrib import admin
    from django.apps import apps
    from django.contrib.admin.sites import AlreadyRegistered
    app_models = apps.get_app_config(app_name).get_models()
    for model in app_models:
        try:
            admin.site.register(model)
        except AlreadyRegistered:
            pass
