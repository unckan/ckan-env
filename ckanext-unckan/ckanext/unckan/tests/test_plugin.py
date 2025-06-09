from ckan import plugins


def test_plugin():
    assert plugins.plugin_loaded("unckan")
