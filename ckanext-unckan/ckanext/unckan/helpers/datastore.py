import logging
from ckan.plugins.toolkit import chained_helper


log = logging.getLogger(__name__)


@chained_helper
def sanitize_id(original_fn, id):
    """ Sobreescribimos el helper del datastore para evitar errores
    original: return str(uuid.UUID(id_))
    """
    try:
        new_id = original_fn(id)
    except Exception:
        log.critical(f"Error sanitize_id in helpers datastore id:{id}")
        raise

    return new_id
