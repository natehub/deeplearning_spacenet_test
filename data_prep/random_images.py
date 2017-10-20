#Script to randomly choose and to copy images into training folders from sqlite database created in from qgis and the data_prep file.

import sqlite3
import shutil
import os

def create_dir(newpath):
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    print("Created directory")

folder = r'C:\Users\Monster\Pictures\Camera Roll\pages'
create_dir(folder)

train = r""+folder+"\\train"
create_dir(train)

valid = r""+folder+"\\valid"
create_dir(valid)

buildings_p_train = r""+train+"\\buildings_p"
create_dir(buildings_p_train)

buildings_k_train = r""+train+"\\buildings_k"
create_dir(buildings_k_train)

buildings_p_val = r""+valid+"\\buildings_p"
create_dir(buildings_p_val)

buildings_k_val =r""+valid+"\\buildings_k"
create_dir(buildings_k_val)


samples = 3000
validate = int(3000 * .10)
print(validate)
conn_k=sqlite3.connect(r'C:\code\deeplearning\data_prep\diff.sqlite')
conn_p=sqlite3.connect(r'C:\code\deeplearning\data_prep_paris\diff.sqlite')
print("connected")


cursor_p =conn_p.execute("SELECT * FROM diff WHERE area < 1150 ORDER BY RANDOM() LIMIT {0};".format(str(samples+validate)))
cursor_k = conn_k.execute("SELECT * FROM diff WHERE area < 1150 ORDER BY RANDOM() LIMIT {0};".format(str(samples+validate)))



for index, row in enumerate(cursor_p):
    if index < validate:
        print(row[2])
        shutil.copy(row[2], buildings_p_val)
    else:
        print(row[2])
        shutil.copy(row[2], buildings_p_train)

for index3, row3 in enumerate(cursor_k):
    if index3 < validate:
        print(row3[2])
        shutil.copy(row3[2], buildings_k_val)
    else:
        print(row3[2])
        shutil.copy(row3[2], buildings_k_train)


#cursor_p =conn_p.execute("SELECT * FROM diff WHERE area > 1500 ORDER BY RANDOM() LIMIT 1;")
#cursor_k = conn_k.execute("SELECT * FROM diff WHERE area > 1500 ORDER BY RANDOM() LIMIT 1;")


#cursor_p =conn_p.execute("alter table diff add selects INTEGER;")
#cursor_k = conn_k.execute("alter table diff add selects INTEGER;")
#cursor_p =conn_p.execute("UPDATE diff SET selects = 0;")
#cursor_k = conn_k.execute("UPDATE diff SET selects = 0;")
#conn_p.commit
#conn_k.commit
#select name from sqlite_master where type = 'table'