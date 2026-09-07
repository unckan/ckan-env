import logging
from ckan import plugins
from ckan.plugins import toolkit
from ckanext.unckan.helpers import base, datastore
from ckanext.unckan.blueprints import blueprints


log = logging.getLogger(__name__)


class UnCKANPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "unckan")
        toolkit.add_ckan_admin_tab(
            config_, "server_terminal.index", "Terminal del servidor", icon="terminal"
        )

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'get_unckan_version': base.get_unckan_version,
            'get_unckan_latest_datasets': base.get_unckan_latest_datasets,
            'get_unckan_most_visited_datasets': base.get_unckan_most_visited_datasets,
            'sanitize_id': datastore.sanitize_id,
        }

    # IBlueprint

    def get_blueprint(self):
        return blueprints.get_blueprints()
