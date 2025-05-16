import logging
from ckan import plugins
from ckan.plugins import toolkit
from ckanext.unckan.helpers import base, datastore
from ckanext.unckan.blueprints.footer_config import footer_blueprint


log = logging.getLogger(__name__)


class UnCKANPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "unckan")

    # Permitir que estos valores se actualicen desde la interfaz web
    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        unicode_safe = toolkit.get_validator('unicode_safe')
        schema.update({
            'ckan.footer.email': [ignore_missing, unicode_safe],
            'ckan.footer.telefono': [ignore_missing, unicode_safe],
            'ckan.footer.direccion': [ignore_missing, unicode_safe],
            'ckan.footer.pagina_oficial': [ignore_missing, unicode_safe],
            'ckan.footer.idioma': [ignore_missing, unicode_safe],
            'ckan.footer.objetivo': [ignore_missing, unicode_safe],
            'ckan.footer.logo': [ignore_missing, unicode_safe],
            'ckan.footer.facebook': [ignore_missing, unicode_safe],
            'ckan.footer.twitter': [ignore_missing, unicode_safe],
            'ckan.footer.instagram': [ignore_missing, unicode_safe],
            'ckan.footer.youtube': [ignore_missing, unicode_safe],
            'ckan.footer.linkedin': [ignore_missing, unicode_safe],
        })
        return schema

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'get_unckan_version': base.get_unckan_version,
            'sanitize_id': datastore.sanitize_id,
            'get_footer_config': self.get_footer_config,
        }

    # IConfigurable
    def configure(self, config):
        """Carga la configuración del footer desde CKAN"""
        self.footer_config = {
            'ckan.footer.email': config.get('ckan.footer.email', 'email@ejemplo.com'),
            'ckan.footer.telefono': config.get('ckan.footer.telefono', '000-000-0000'),
            'ckan.footer.direccion': config.get('ckan.footer.direccion', 'Dirección no definida'),
            'ckan.footer.pagina_oficial': config.get('ckan.footer.pagina_oficial', 'https://ejemplo.com'),
            'ckan.footer.idioma': config.get('ckan.footer.idioma', 'Español'),
            'ckan.footer.objetivo': config.get('ckan.footer.objetivo', 'Nuestro objetivo es.'),
            'ckan.footer.logo': config.get('ckan.footer.logo', '/logo_footer_unc.png'),
            'ckan.footer.facebook': config.get('ckan.footer.facebook', 'https://facebook.com'),
            'ckan.footer.twitter': config.get('ckan.footer.twitter', 'https://twitter.com'),
            'ckan.footer.instagram': config.get('ckan.footer.instagram', 'https://instagram.com'),
            'ckan.footer.youtube': config.get('ckan.footer.youtube', 'https://youtube.com'),
            'ckan.footer.linkedin': config.get('ckan.footer.linkedin', 'https://linkedin.com')
        }

    def get_footer_config(self):
        """Devuelve los valores del footer para usarlos en las plantillas"""
        footer_config = {}

        for key in self.footer_config.keys():
            # Obtiene el valor directamente de la configuración de CKAN
            value = toolkit.config.get(key, self.footer_config[key])

            # Limpiar el valor del logo si tiene comillas
            if key == 'ckan.footer.logo' and value:
                value = value.strip('"').strip("'")
            footer_config[key] = value
        return footer_config

    def get_blueprint(self):
        """Agrega una ruta para manejar la configuración desde Flask"""
        return footer_blueprint
