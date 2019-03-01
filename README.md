# api-sales

The goal of the assignment is to develop an API to get the number of a product sold during last n days.
Input file contains following format:

```{"Id": customer id, "products": list of product_ids associated with the transactions}``` 
 
 
 The whole design contains 3 parts:
 * Spark for loading database to influxDB
 * InfluxDB to store data
 * Flask API
 
  
### Design consideration/assumptions
 
 * Spark(local mode) is selected for scalability over plain python/pandas.
 * InfluxDB (time series database) is selected for:
    * Scalability
    * Data is indexed using datetime, which is useful for datetime query. e.g. item sold last n days/months/years 
      or between time periods 
    * Can be integrated with Grafana for dashboard
 *  API considerations:
    * Rate limiting for API (60 requests per minute)
    * Basic username password authentication for 1 user
    * Can only request one item per request
    * Returns quantity of an item sold for last 30 days
    * Returns all items present in the database 
    
###The details of the files:
 * loader.py : pyspark script to read input file and load data to the InfluxDB
 * testing_spark.py: test cases for spark job
 * api_sales.py: Run API using Flask module with endpoints http://127.0.0.1:5000/item/<itemID> and http://127.0.0.1:5000/itemlist
    * /item/\<itemeID\> returns quantity of an item sold
    * /itemlist returns the list of items sold for last 30 days
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
    Flask-Limiter==1.0.1
    Flask-HTTPAuth==3.2.4
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

``` 
    spark-submit loader.py 20190207_transactions.json 
``` 
2. API requests
```
     curl -X GET http://127.0.0.1:5000/itemlist --user admin:adminpassword
     curl -X GET http://127.0.0.1:5000/item/<itemID> --user admin:adminpassword
```
3. Testing

    For testing, choose sales_api_test as the measurement from config.yml
    
``` 
    python testing_spark.py
    python testing.py
```
 
 
### Future additions
* Advanced authentication using database and encrypted password/tokens
* Add datetime filter in query/route
* Add tags(for influxdb) like the type for items to track more insights about types of the item sold 