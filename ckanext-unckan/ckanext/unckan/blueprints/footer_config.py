import os
import logging
from flask import Blueprint, redirect, flash, request
from werkzeug.utils import secure_filename
from ckan.plugins import toolkit
from ckan import model

log = logging.getLogger(__name__)

blueprint = Blueprint('footer_config', __name__, url_prefix='/ckan-admin')

# Carpeta donde se guardarán los logos subidos (ajústala según tu configuración)
UPLOAD_FOLDER = '/app/unckan/public/'
DEFAULT_LOGO = '/ckanext/unckan/public/logo_footer_unc.png'

@blueprint.route('/footer-config', methods=['GET', 'POST'])
def footer_config():
    """Maneja la configuración del footer en el admin"""
    if not toolkit.check_access('sysadmin'):
        return toolkit.abort(403, 'Solo los administradores pueden configurar el footer')

    if request.method == 'POST':
        # Si el usuario presiona "Reset", restablecer valores por defecto
        if 'reset' in request.form:
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
                # Se usa `model.set_system_info()` para persistir valores
                model.Session.query(model.SystemInfo).filter_by(key=key).delete()  # Borra valor previo
                model.set_system_info(key, value)  # Inserta el nuevo valor
                toolkit.config[key] = value  # Actualiza configuración en ejecución

            model.Session.commit()
            flash('Configuración restablecida a los valores predeterminados', 'success')
            return redirect('/ckan-admin/config')

        # Manejo de subida de logo
        if 'ckan.footer.logo' in request.files:
            file = request.files['ckan.footer.logo']
            if file.filename:
                file_path = os.path.join(UPLOAD_FOLDER, "logo_footer_unc.png")

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
