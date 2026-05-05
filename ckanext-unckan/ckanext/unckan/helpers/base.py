import ckan.plugins.toolkit as toolkit
from ckan.common import config


def get_unckan_version():
    """ Get the UNCKAN extnsion version from CKAN_UNI_VERSION """
    return config.get('ckanext.unckan.version')


def get_unckan_most_visited_datasets(limit=5):
    """ Retorna los datasets más visitados usando el tracking built-in de CKAN """
    data_dict = {
        'rows': limit,
        'sort': 'views_total desc',
        'include_private': False,
    }
    try:
        result = toolkit.get_action('package_search')({}, data_dict)
    except Exception:
        return []
    datasets = []
    for pkg in result.get('results', []):
        views = pkg.get('tracking_summary', {}).get('total', 0)
        if not views:
            continue
        notes = pkg.get('notes', '') or ''
        description = (notes[:200] + '...') if len(notes) > 200 else notes
        datasets.append({
            'id': pkg['id'],
            'name': pkg['name'],
            'title': pkg.get('title', pkg['name']),
            'description': description,
            'url': toolkit.url_for('dataset.read', id=pkg['name']),
            'organization': pkg.get('organization', {}).get('title', ''),
            'num_resources': pkg.get('num_resources', 0),
            'views_total': views,
        })
    return datasets


def get_unckan_latest_datasets(limit=5):
    """ Retorna los últimos datasets modificados """
    data_dict = {
        'rows': limit,
        'sort': 'metadata_modified desc',
        'include_private': False,
    }
    result = toolkit.get_action('package_search')({}, data_dict)
    datasets = []
    for pkg in result.get('results', []):
        notes = pkg.get('notes', '') or ''
        description = (notes[:200] + '...') if len(notes) > 200 else notes
        datasets.append({
            'id': pkg['id'],
            'name': pkg['name'],
            'title': pkg.get('title', pkg['name']),
            'description': description,
            'url': toolkit.url_for('dataset.read', id=pkg['name']),
            'organization': pkg.get('organization', {}).get('title', ''),
            'num_resources': pkg.get('num_resources', 0),
            'metadata_modified': pkg.get('metadata_modified', ''),
        })
    return datasets
