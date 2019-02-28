from pyspark import SparkConf, SparkContext
from loader import Loader
import unittest


class SparkTest(unittest.TestCase):

    @classmethod
    def create_spark_context(cls):
        conf = SparkConf().setMaster("local").setAppName('Sales_loader_tester')
        return SparkContext(conf=conf)

    @classmethod
    def setUpClass(cls):
        # cls.supress_logging()
        cls.loader = Loader()
        cls.sc = cls.create_spark_context()

    @classmethod
    def tearDownClass(cls):
        cls.sc.stop()


class SparkUnitTest(SparkTest):
    def test_init_mapping(self):
        test_rdd = self.sc.parallelize(['{"id": 28, "products": [58, 48, 870]}',
                                        '{"id": 29, "products": [228, 90, 13]}',
                                        '{"id": 30, "products": [204, 90]}',
                                        '{"id": 31, "products": []}'])
        results = test_rdd.map(Loader._init_mapping).collect()
        expected_results = [[58, 48, 870], [228, 90, 13], [204, 90], []]
        self.assertEqual(results, expected_results)

    def test_transform(self):
        test_rdd = self.sc.parallelize([[58, 58, 87], [58, 87, 13]])
        loader_out = self.loader._transform(test_rdd)
        expected_result = [{'measurement': 'sales_api_test', 'tags': {'item': '58'}, 'time': '2019-02-07', 'fields': {'quantity': 3}},
                           {'measurement': 'sales_api_test', 'tags': {'item': '87'}, 'time': '2019-02-07', 'fields': {'quantity': 2}},
                           {'measurement': 'sales_api_test', 'tags': {'item': '13'}, 'time': '2019-02-07', 'fields': {'quantity': 1}}]

        self.assertEqual(loader_out.collect(), expected_result)

    def test_influx_loader(self):
        test_rdd = self.sc.parallelize([{'measurement': 'sales_api_test', 'tags': {'item': '58'}, 'time': '2019-02-07', 'fields': {'quantity': 3}},
                                        {'measurement': 'sales_api_test', 'tags': {'item': '87'}, 'time': '2019-02-07', 'fields': {'quantity': 2}}])
        test_rdd.foreachPartition(self.loader._influxdb_loader)
        result = self.loader._influxdb_client.query('select * from sales_api_test')
        self.assertEqual(len(list(result.get_points())), 2)


if __name__ == '__main__':
    unittest.main()