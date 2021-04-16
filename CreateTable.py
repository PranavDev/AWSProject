import pymysql

conn = pymysql.connect(
    host='netflix.cm7noqu6gj7y.us-east-1.rds.amazonaws.com',
    port=3306,
    user='phd24',
    password='Phd240997#',
    db='netflix')

cursor = conn.cursor()
create_table = "create table Netflix_Users (username varchar(100),email varchar(100),password varchar(100))"
cursor.execute(create_table)
