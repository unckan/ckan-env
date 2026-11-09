from sqlalchemy import func

from ckan import model
import ckan.plugins.toolkit as toolkit
from ckanext.api_tracking.models import TrackingUsage
from ckan.common import config


def get_unckan_version():
    """ Get the UNCKAN extnsion version from CKAN_UNI_VERSION """
    return config.get('ckanext.unckan.version')


def get_unckan_most_visited_datasets(limit=5):
    """Retorna datasets públicos activos por visitas web acumuladas de api-tracking."""
    if limit <= 0:
        return []
    views = func.count(TrackingUsage.id).label('views')
    popular = (
        model.Session.query(model.Package.id, views)
        .join(TrackingUsage, TrackingUsage.object_id == model.Package.id)
        .filter(
            model.Package.state == 'active',
            model.Package.private.is_(False),
            model.Package.type == 'dataset',
            TrackingUsage.object_type == 'dataset',
            TrackingUsage.tracking_type == 'ui',
            TrackingUsage.tracking_sub_type == 'show',
        )
        .group_by(model.Package.id)
        .order_by(views.desc(), model.Package.id)
        .limit(limit)
        .all()
    )
    datasets = []
    for package_id, views in popular:
        pkg = toolkit.get_action('package_show')({}, {'id': package_id})
        notes = pkg.get('notes', '') or ''
        description = (notes[:200] + '...') if len(notes) > 200 else notes
        datasets.append({
            'id': pkg['id'],
            'name': pkg['name'],
            'title': pkg.get('title', pkg['name']),
            'description': description,
            'url': toolkit.url_for('dataset.read', id=pkg['name']),
            'organization': (pkg.get('organization') or {}).get('title', ''),
            'num_resources': pkg.get('num_resources', 0),
            'visits': views,
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
            'organization': (pkg.get('organization') or {}).get('title', ''),
            'num_resources': pkg.get('num_resources', 0),
            'metadata_modified': pkg.get('metadata_modified', ''),
        })
    return datasets
