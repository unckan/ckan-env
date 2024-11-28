from ckan.common import config


def get_unckan_version():
    """ Get the UNCKAN extnsion version from CKAN_UNI_VERSION """
    return config.get('ckanext.unckan.version')
