import psycopg2
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


def query_database():
    """ Realiza una consulta a la base de datos y retorna los resultados """
    conn = psycopg2.connect(
        dbname="tu_base",
        user="tu_usuario",
        password="tu_password",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM tu_tabla LIMIT 10")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{"columna1": row[0], "columna2": row[1]} for row in rows]


class DbqueryPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "dbquery")

    def get_actions(self):
        """ Registra la acción custom_query """
        return {
            "custom_query": self.custom_query
        }

    def custom_query(self, context, data_dict):
        """ Realiza una consulta a la base de datos y retorna los resultados """
        return query_database()
