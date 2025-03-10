import logging
from flask import Blueprint, redirect, flash
from ckan.plugins import toolkit

log = logging.getLogger(__name__)

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

    # Get the footer config from the plugin
    from ckanext.unckan.plugin import UnCKANPlugin
    plugin = UnCKANPlugin()
    return toolkit.render('admin/config.html', config=plugin.get_footer_config())
