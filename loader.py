from influxdb import InfluxDBClient
from pyspark import SparkConf, SparkContext
import json
import yaml
import sys
from datetime import datetime

class Loader(object):
    """ Loader transforms the input file and loads data into InfluxDB
        :param input_file : input transactions file
    """
    def __init__(self, input_file='20190207_transactions.json'):
        param_file = 'config.yml'
        with open(param_file, 'r') as ymlfile:
            self._param_config = yaml.load(ymlfile)
        self._influxdb_client = InfluxDBClient(self._param_config["INFLUXDB_URL"],
                                               self._param_config["INFLUXDB_PORT"],
                                               self._param_config["INFLUXDB_LOGIN"],
                                               self._param_config["INFLUXDB_PASS"],
                                               self._param_config["INFLUXDB_DATABASE"]
                                               )
        self._input_file = input_file
        self.current_date = datetime.strptime(input_file.split('_')[0], '%Y%m%d').strftime('%Y-%m-%d')

    @staticmethod
    def _init_mapping(line):
        """Select lists of items from each record"""
        data = json.loads(line)
        return data['products']

    def _influxdb_loader(self, rows):
        """Loads data points to Influxdb"""
        self._influxdb_client.write_points(rows)

    def _transform(self, rdd_in):
        """ Converts rdd of items list to InfluxDB format with tag=item and field=quantity
        """
        item_rdd = rdd_in.flatMap(lambda x: x)
        final_map = item_rdd.map(lambda x: (x, 1))
        final_output = final_map.reduceByKey(lambda x, y: x + y)
        rdd_out = final_output.map(lambda x: {
            "measurement": self._param_config['MEASUREMENT'],
            "tags": {
                "item": str(x[0]),
            },
            "time": self.current_date,
            "fields": {
                "quantity": x[1],
            }
        })
        return rdd_out

    def run(self, sc):
        input_rdd = sc.textFile(self._input_file)
        mapped_rdd = input_rdd.map(self._init_mapping)

        """Cached the transformed rdd"""
        loader_out = self._transform(mapped_rdd).cache()

        """use foreachPartition to create one database connection per partition"""
        loader_out.foreachPartition(self._influxdb_loader)


if __name__ == '__main__':
    conf = SparkConf().setMaster("local").setAppName('Sales_loader')
    sc = SparkContext(conf=conf)
    loader = Loader(sys.argv[1])
    loader.run(sc)
