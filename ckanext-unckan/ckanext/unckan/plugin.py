import logging
from ckan import plugins
from ckan.plugins import toolkit
from ckanext.unckan.helpers import base


log = logging.getLogger(__name__)


class UnCKANPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "unckan")

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'get_unckan_version': base.get_unckan_version
        }
