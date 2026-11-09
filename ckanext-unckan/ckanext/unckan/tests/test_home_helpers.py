import pytest

from ckan import model, plugins
from ckan.plugins import toolkit
from ckan.tests import factories
from ckanext.api_tracking.models import TrackingUsage
from ckanext.unckan.helpers.base import get_unckan_most_visited_datasets


def add_visits(dataset, count, **overrides):
    values = dict(
        object_id=dataset['id'], object_type='dataset',
        tracking_type='ui', tracking_sub_type='show',
    )
    values.update(overrides)
    for _ in range(count):
        model.Session.add(TrackingUsage(**values))
    model.Session.commit()


@pytest.mark.usefixtures('clean_db')
class TestMostVisitedDatasets:
    def test_ranking_and_card_data(self, app):
        org = factories.Organization(title='Universidad')
        first = factories.Dataset(owner_org=org['id'], title='Popular', notes='a' * 201)
        factories.Resource(package_id=first['id'])
        second = factories.Dataset()
        factories.Dataset()  # No visits: must not appear.
        add_visits(second, 2)
        add_visits(first, 3)

        with app.flask_app.test_request_context('/'):
            result = get_unckan_most_visited_datasets()
            assert [row['id'] for row in result] == [first['id'], second['id']]
            assert [row['visits'] for row in result] == [3, 2]
            assert result[0]['title'] == 'Popular'
            assert result[0]['description'] == 'a' * 200 + '...'
            assert result[0]['organization'] == 'Universidad'
            assert result[0]['num_resources'] == 1
            assert result[0]['url'] == toolkit.url_for('dataset.read', id=first['name'])
            assert len(get_unckan_most_visited_datasets(limit=1)) == 1
            assert get_unckan_most_visited_datasets(limit=0) == []

    def test_excludes_hidden_datasets_and_other_events_before_limit(self, app):
        org = factories.Organization()
        private = factories.Dataset(owner_org=org['id'], private=True)
        deleted = factories.Dataset()
        public = factories.Dataset()
        add_visits(private, 10)
        add_visits(deleted, 10)
        toolkit.get_action('package_delete')(
            {'ignore_auth': True, 'user': factories.Sysadmin()['name']}, {'id': deleted['id']},
        )
        add_visits(public, 1)
        for overrides in [
            {'tracking_type': 'api'}, {'tracking_sub_type': 'edit'},
            {'tracking_sub_type': 'home'}, {'object_type': 'resource'},
            {'object_id': 'missing-dataset'},
        ]:
            add_visits(public, 10, **overrides)

        with app.flask_app.test_request_context('/'):
            result = get_unckan_most_visited_datasets(limit=1)
            assert [(row['id'], row['visits']) for row in result] == [(public['id'], 1)]

    def test_no_visits(self):
        factories.Dataset()
        assert get_unckan_most_visited_datasets() == []

    def test_home_uses_visits_and_catalog_link(self, app):
        dataset = factories.Dataset(title='Dataset popular')
        add_visits(dataset, 7)
        response = app.get('/')
        assert 'Dataset popular' in response
        assert '7 visitas' in response
        assert 'views_total' not in response.text
        assert not plugins.plugin_loaded('tracking')
