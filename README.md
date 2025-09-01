There are 3 files:
the first file  is the setup file which crweates a vpc with  a publiac and a private subnet
there is a security group attached to the vpc which allows the https and https traffic
the database is in rds format using the mysql engine
the ec2 instance is of the amazon linux image

the secomd file is the encrypt file you can run that file using flask run or direactly using python encrypt.py
it uses fernet library of the cryptography to encrypt and decrypt
the connection to the rds in the aws is made using the pymysql

in the third file is creation of the iam role which has full access to all the databases in the aws 
