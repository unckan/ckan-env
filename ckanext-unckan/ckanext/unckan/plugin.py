import logging
from ckan import plugins
from ckan.plugins import toolkit
from ckanext.unckan.helpers import base, datastore
from flask import Blueprint, request, redirect


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
        """Carga la configuración del footer desde ckan.ini"""
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
        return self.footer_config

    def get_blueprint(self):
        """Agrega una ruta para manejar la configuración desde Flask"""
        blueprint = Blueprint('footer_config', __name__, url_prefix='/ckan-admin')

        @blueprint.route('/footer-config', methods=['GET', 'POST'])
        def footer_config():
            """Maneja la configuración del footer en el admin"""
            if request.method == 'POST':
                # Guardar los valores enviados
                new_config = request.form.to_dict()

                # Actualizar ckan.ini en memoria
                for key, value in new_config.items():
                    toolkit.config[key] = value
                    log.info(f'Actualizado: {key} = {value}')

                return redirect('/ckan-admin/config')

            return toolkit.render('admin/config.html', config=toolkit.config)

        return blueprint
