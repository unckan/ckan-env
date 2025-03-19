import logging
from flask import Blueprint, redirect, flash
from ckan.plugins import toolkit
from ckan import model

log = logging.getLogger(__name__)

blueprint = Blueprint('footer_config', __name__, url_prefix='/ckan-admin')


@blueprint.route('/footer-config', methods=['GET', 'POST'])
def footer_config():
    """Maneja la configuración del footer en el admin"""
    if not toolkit.check_access('sysadmin'):
        return toolkit.abort(403, 'Solo los administradores pueden configurar el footer')

    if toolkit.request.method == 'POST':
        # Get form data
        form_dict = toolkit.request.form.to_dict()

        # Actualizar cada opción de configuración individualmente
        for key, value in form_dict.items():
            if key.startswith('ckan.footer.'):
                try:
                    # Usar el modelo directamente para actualizar la configuración
                    model.set_system_info(key, value)
                    toolkit.config[key] = value
                    log.info(f'Configuración guardada correctamente: {key}')
                except Exception as e:
                    log.error(f'Error al guardar {key}: {str(e)}')

        model.Session.commit()
        flash('Configuración del footer actualizada con éxito', 'success')
        return redirect('/ckan-admin/config')

    # Get the footer config
    from ckanext.unckan.plugin import UnCKANPlugin
    plugin = UnCKANPlugin()
    return toolkit.render('admin/config.html', config=plugin.get_footer_config())
