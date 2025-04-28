import os
import logging
from flask import Blueprint, redirect, flash, request
from ckan.plugins import toolkit
from ckan import model

log = logging.getLogger(__name__)

footer_blueprint = Blueprint('footer_config', __name__, url_prefix='/ckan-admin')

# Carpeta donde se guardarán los logos subidos (ajústala según tu configuración)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'public')
DEFAULT_LOGO = '/base/images/logo_footer_unc.png'


@footer_blueprint.route('/reset-footer-config', methods=['GET', 'POST'])
def reset_footer_config():
    """Restablece la configuración del footer a los valores predeterminados"""
    context = {'user': toolkit.c.user}
    try:
        toolkit.check_access('sysadmin', context)
    except toolkit.NotAuthorized:
        return toolkit.abort(403, 'Solo los administradores pueden configurar el footer')

    try:
        default_config = {
            'ckan.footer.email': 'email@gmail.com',
            'ckan.footer.telefono': '0555-9999999',
            'ckan.footer.direccion': 'Av. Nombre Calle, Ciudad.',
            'ckan.footer.pagina_oficial': 'https://www.institución.edu.ar/contactenos',
            'ckan.footer.idioma': 'español',
            'ckan.footer.objetivo': 'Nuestro objetivo es.',
            'ckan.footer.logo': DEFAULT_LOGO,
            'ckan.footer.facebook': 'https://www.facebook.com/',
            'ckan.footer.twitter': 'https://twitter.com/',
            'ckan.footer.instagram': 'https://www.instagram.com/',
            'ckan.footer.youtube': 'https://www.youtube.com/',
            'ckan.footer.linkedin': 'https://www.linkedin.com/'
        }

        for key, value in default_config.items():
            model.Session.query(model.SystemInfo).filter_by(key=key).delete()
            model.set_system_info(key, value)
            toolkit.config[key] = value

        model.Session.commit()
        flash('Configuración del footer restablecida con éxito', 'success')
        log.info('Configuración del footer restablecida correctamente')
    except Exception as e:
        model.Session.rollback()
        flash('Error al restablecer la configuración del footer: ' + str(e), 'error')
        log.error(f'Error al restablecer la configuración del footer: {str(e)}')

    return redirect('/ckan-admin/config')


@footer_blueprint.route('/footer-config', methods=['GET', 'POST'])
def footer_config():
    """Maneja la configuración del footer en el admin"""
    context = {'user': toolkit.c.user}
    try:
        toolkit.check_access('sysadmin', context)
    except toolkit.NotAuthorized:
        return toolkit.abort(403, 'Solo los administradores pueden configurar el footer')

    if request.method == 'POST':
        # Manejo de subida de logo
        if 'ckan.footer.logo' in request.files:
            file = request.files['ckan.footer.logo']
            if file.filename:
                file_path = os.path.join(UPLOAD_FOLDER, 'logo_footer_unc.png')

                try:
                    file.save(file_path)
                    log.info(f'Nuevo logo guardado en {file_path}')

                    # Guardar la ruta accesible desde CKAN
                    model.Session.query(model.SystemInfo).filter_by(key='ckan.footer.logo').delete()
                    model.set_system_info('ckan.footer.logo', DEFAULT_LOGO)
                    toolkit.config['ckan.footer.logo'] = DEFAULT_LOGO
                except Exception as e:
                    log.error(f'Error guardando el logo: {str(e)}')
                    flash('Error al subir el logo', 'danger')

        # Guardar otros valores del formulario
        form_dict = request.form.to_dict()
        for key, value in form_dict.items():
            if key.startswith('ckan.footer.'):
                model.Session.query(model.SystemInfo).filter_by(key=key).delete()
                model.set_system_info(key, value)
                toolkit.config[key] = value

        model.Session.commit()
        flash('Configuración del footer actualizada con éxito', 'success')
        return redirect('/ckan-admin/config')

    # Obtener la configuración actual del plugin
    from ckanext.unckan.plugin import UnCKANPlugin
    plugin = UnCKANPlugin()
    return toolkit.render('admin/config.html', config=plugin.get_footer_config())
