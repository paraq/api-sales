from flask import Flask
from flask_restful import Api, Resource
from influxdb import InfluxDBClient
import yaml
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


class ApiSales(Resource):
    def __init__(self):
        param_file = 'config.yml'
        with open(param_file, 'r') as ymlfile:
            self.param_config = yaml.load(ymlfile)
        self.influxdb_client = InfluxDBClient(self.param_config["INFLUXDB_URL"],
                                              self.param_config["INFLUXDB_PORT"],
                                              self.param_config["INFLUXDB_LOGIN"],
                                              self.param_config["INFLUXDB_PASS"],
                                              self.param_config["INFLUXDB_DATABASE"]
                                              )

    def get(self, id):
        query = "select * from " + self.param_config['MEASUREMENT'] + " where item=\'"+str(id)+"\'"
        result = self.influxdb_client.query(query)
        qdata = list(result.get_points())
        if not qdata:
            return "Item not found", 404
        else:
            return (qdata[0]['quantity']), 200


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["60 per minute"],
    )
    api.add_resource(ApiSales, "/item/<int:id>")
    app.run(threaded=True)
