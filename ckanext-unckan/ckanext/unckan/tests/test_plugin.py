from ckan import plugins


def test_plugin():
    assert plugins.plugin_loaded("unckan")


def test_server_terminal_blueprint_is_registered():
    plugin = plugins.get_plugin("unckan")
    assert plugin.get_blueprint()[0].name == "server_terminal"
