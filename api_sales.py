from flask import Flask
from flask_restful import Api, Resource
from influxdb import InfluxDBClient
import yaml
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_httpauth import HTTPBasicAuth

"""Authentication part"""
auth = HTTPBasicAuth()
USER_DATA = {"admin": "adminpassword"}


@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password


class ApiSales(Resource):
    """
        Api creates route http://127.0.0.1:5000/item/<item_id>
        GET: Returns quantity of item ordered
    """
    def __init__(self):
        param_file = 'config.yml'
        with open(param_file, 'r') as ymlfile:
            self._param_config = yaml.load(ymlfile)
        self._influxdb_client = InfluxDBClient(self._param_config["INFLUXDB_URL"],
                                              self._param_config["INFLUXDB_PORT"],
                                              self._param_config["INFLUXDB_LOGIN"],
                                              self._param_config["INFLUXDB_PASS"],
                                              self._param_config["INFLUXDB_DATABASE"]
                                              )

    @auth.login_required
    def get(self, id):
        """Return quantity of item ordered"""
        query = "select SUM(quantity) from " + self._param_config['MEASUREMENT'] + " where item=\'"+str(id)+"\'" \
                "and time >= now() - 30d"
        result = self._influxdb_client.query(query)
        qdata = list(result.get_points())
        if not qdata:
            return "Item not found", 404
        else:
            return (qdata[0]['sum']), 200


class ApiItemList(ApiSales):
    """
            Api creates route http://127.0.0.1:5000/itemlist
            GET: Returns list of items ordered
    """

    @auth.login_required
    def get(self):
        items = []
        query = "select * from " + self._param_config['MEASUREMENT']
        result = self._influxdb_client.query(query)
        qdata = list(result.get_points())
        for data in qdata:
            items.append(int(data['item']))
        return (items), 200


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)

    """Limit the amount of requests to avoid spamming"""
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["60 per minute"],
    )

    """Add routes"""
    api.add_resource(ApiSales, "/item/<int:id>")
    api.add_resource(ApiItemList, "/itemlist")
    app.run(threaded=True)
