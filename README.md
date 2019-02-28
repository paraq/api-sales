# api-sales

The goal of the assignment is to develop an API to get the number of a product sold during last days.
Input file contains following format:

```{"Id": customer id, "products": list of product_ids associated with the transactions}``` 
 
 
 The whole design contains of 3 parts:
 * Spark for loading database to influxDB
 * InfluxDB to store data
 * API
 
 The details of the files:
 * loader.py : pyspark script to read input file and load data to the InfluxDB
 * testing_spark.py: test cases for spark job
 * api_sales.py: Run API using Flask module with endpoints http://127.0.0.1:5000/item/<itemID> and http://127.0.0.1:5000/itemlist
    * /item/<itemeID> returns quantity of items sold
    * /itemlist returns the list of items sold
 * testing.py: test cases for API endpoints
 * 20190207_transactions.json: Input data file
 * config.yml: Parameter file
 
 ### Dependencies
 
 The python modules needed:
```
pyspark==2.4.0
Flask-RESTful==0.3.7
flask==1.0.2
influxdb==4.1.1
```  

Other dependencies:

* [spark 2.4.0](https://spark.apache.org/)
* [InfluxDB 1.6.4](https://www.influxdata.com/) 

Database setup after installing InfluxDB:

```
influx -username [username] -password [password] -precision rfc3339
create database sales
```

### Commands
1. Loading file

    spark-submit loader.py 20190207_transactions.json 
2. API requests
    * curl http://127.0.0.1:5000/itemlist
    * curl http://127.0.0.1:5000/item/<itemID>
3. Testing

    For testing, choose sales_api_test as the measurement from config.yml
    * python testing_spark.py
    * python testing.py

 
 
### Design consideration
 
 * Spark is selected for scalability over only python/pandas.
 * InfluxDB (time series database) is selected for following:
    * Scalable
    * Data is index using datetime, which is useful for datetime query. e.g. item sold last n days/months/years 
      or between time periods 
    * Can be integrated with grafana for dashboard
 *  API considerations:
    * Rate limiting for API
 
### Future additions
* Authentication
* Add datetime filter in query/route
* Add tags(for influxdb) like type for items to track more insights about types of item sold 