from pyspark import SparkContext

sc = SparkContext("local", "RDD example")

data = [12, 13, 14, 15, 16, 17, 18, 19, 20]
rdd = sc.parallelize(data)

sqr_rdd = rdd.map(lambda x: x**2)

res = sqr_rdd.collect()
print(res)
sc.stop()
