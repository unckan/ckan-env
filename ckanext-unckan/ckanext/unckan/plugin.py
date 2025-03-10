import logging
from ckan import plugins
from ckan.plugins import toolkit
from ckanext.unckan.helpers import base, datastore
from flask import Blueprint, redirect, flash


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
            'ckan.footer.logo': config.get('ckan.footer.logo', '/logo_footer.png'),
            'ckan.footer.facebook': config.get('ckan.footer.facebook', 'https://facebook.com'),
            'ckan.footer.twitter': config.get('ckan.footer.twitter', 'https://twitter.com'),
            'ckan.footer.instagram': config.get('ckan.footer.instagram', 'https://instagram.com'),
            'ckan.footer.youtube': config.get('ckan.footer.youtube', 'https://youtube.com'),
            'ckan.footer.linkedin': config.get('ckan.footer.linkedin', 'https://linkedin.com')
        }

    # ITemplateHelpers

    def get_footer_config(self):
        """Devuelve los valores del footer para usarlos en las plantillas"""
        footer_config = {}
        keys = self.footer_config.keys()  # Usa las mismas claves definidas en `self.footer_config`

        for key in keys:
            try:
                result = toolkit.get_action('config_option_show')({}, {'key': key})
                footer_config[key] = result['value']
            except Exception as e:
                log.error(f'Error al obtener {key}: {str(e)}')
                footer_config[key] = self.footer_config[key]  # Usa valor predeterminado si no existe en la BD

        return footer_config

    def get_blueprint(self):
        """Agrega una ruta para manejar la configuración desde Flask"""
        blueprint = Blueprint('footer_config', __name__, url_prefix='/ckan-admin')

        @blueprint.route('/footer-config', methods=['GET', 'POST'])
        def footer_config():
            """Maneja la configuración del footer en el admin"""
            if toolkit.request.method == 'POST':
                new_config = toolkit.request.form.to_dict()

                # Guardar cambios en CKAN usando `config_option_update`
                for key, value in new_config.items():
                    try:
                        toolkit.get_action('config_option_update')({}, {'key': key, 'value': value})
                        log.info(f'Configuración guardada: {key} = {value}')
                    except Exception as e:
                        log.error(f'Error al guardar {key}: {str(e)}')

                flash('Configuración actualizada con éxito', 'success')
                return redirect('/ckan-admin/config')

            return toolkit.render('admin/config.html', config=self.get_footer_config())

        return blueprint
