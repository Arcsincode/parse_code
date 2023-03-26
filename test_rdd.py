# coding:utf8
import os
from pyspark import SparkConf,SparkContext

# os.environ['JAVA_HOME'] = "/export/server/jdk1.8.0_361"
# os.environ['PATH'] = "$PATH:$JAVA_HOME/bin"
# os.environ['CLASSPATH'] = ".:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar"
# os.environ['SPARK_HOME'] = "/export/server/spark-3.3.1-bin-hadoop3"
# os.environ['HADOOP_CONF_DIR'] = "$HADOOP_HOME/etc/hadoop"
# os.environ['PYSPARK_PYTHON'] = "/usr/bin/venv/pyspark/bin/python3.10"

'''
                                    
export HADOOP_HOME=/export/server/hadoop-3.3.0    
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin                                                 
export SPARK_HOME=/export/server/spark-3.3.1-bin-hadoop3
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
#export PYSPARK_PYTHON=/home/arcsinszy/App/anaconda/anaconda3/envs/pyspark/bin/python3.10
export PYSPARK_PYTHON=/usr/bin/venv/pyspark/bin/python3.10
'''


conf = SparkConf().setMaster("Local[*]").setAppName("Hello")
sc = SparkContext(conf=conf)
