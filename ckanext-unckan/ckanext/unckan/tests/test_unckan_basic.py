from ckan.lib.helpers import url_for
from ckan.tests import factories


class TestUnCKANPluginUsageBasic:
    """ Test basic unckan from requests
    """

    def test_api_get_package_show(self, app):
        """ Test user for api package_show """
        user_with_token = factories.UserWithToken()
        dataset = factories.Dataset()
        url = url_for("api.action", ver=3, logic_function="package_show", id=dataset["id"])
        auth = {"Authorization": user_with_token['token']}
        response = app.get(url, extra_environ=auth)
        assert response.status_code == 200
        assert response.json["result"]["id"] == dataset["id"]

    def test_api_get_organization_show(self, app):
        """ Test user for api organization_show """
        user_with_token = factories.UserWithToken()
        org = factories.Organization()
        url = url_for("api.action", ver=3, logic_function="organization_show", id=org["id"])
        auth = {"Authorization": user_with_token['token']}
        response = app.get(url, extra_environ=auth)
        assert response.status_code == 200
        assert response.json["result"]["id"] == org["id"]

    def test_api_get_resource_show(self, app):
        """ Test user for api package_show """
        user_with_token = factories.UserWithToken()
        resource = factories.Resource()
        url = url_for("api.action", ver=3, logic_function="resource_show", id=resource["id"])
        auth = {"Authorization": user_with_token['token']}
        response = app.get(url, extra_environ=auth)
        assert response.status_code == 200
        assert response.json["result"]["id"] == resource["id"]

    def test_ui_get_dataset_show(self, app):
        """ Test user for dataset/NAME """
        user_with_token = factories.UserWithToken()
        dataset = factories.Dataset()
        url = url_for("dataset.read", id=dataset["id"])
        auth = {"Authorization": user_with_token['token']}
        response = app.get(url, extra_environ=auth)
        assert response.status_code == 200
        assert dataset["id"] in response.body

    def test_ui_get_resource_show(self, app):
        """ Test user for dataset/NAME/resource/ID """
        user_with_token = factories.UserWithToken()
        resource = factories.Resource()
        dataset_id = resource["package_id"]
        url = url_for("dataset_resource.read", id=dataset_id, resource_id=resource["id"])
        auth = {"Authorization": user_with_token['token']}
        response = app.get(url, extra_environ=auth)
        assert response.status_code == 200
        assert resource["id"] in response.body

    def test_ui_get_dataset_home(self, app):
        """ Test user for dataset/NAME """
        user_with_token = factories.UserWithToken()
        url = url_for("dataset.search")
        auth = {"Authorization": user_with_token['token']}
        response = app.get(url, extra_environ=auth)
        assert response.status_code == 200
        assert "Datasets" in response.body

    def test_ui_get_organization_show(self, app):
        """ Test user for organization/NAME """
        user_with_token = factories.UserWithToken()
        org = factories.Organization()
        url = url_for("organization.read", id=org["id"])
        auth = {"Authorization": user_with_token['token']}
        response = app.get(url, extra_environ=auth)
        assert response.status_code == 200
        assert org["id"] in response.body

    def test_ui_get_organization_home(self, app):
        """ Test user for organization/NAME """
        user_with_token = factories.UserWithToken()
        url = url_for("organization.index")
        auth = {"Authorization": user_with_token['token']}
        response = app.get(url, extra_environ=auth)
        assert response.status_code == 200
        assert "Organizations" in response.body
