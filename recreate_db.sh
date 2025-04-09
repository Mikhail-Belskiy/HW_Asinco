export PGPASSWORD=Mb20041995
psql --host 127.0.0.1 -p 5431 -U postgres -d postgres -c 'drop database swapi'
psql --host 127.0.0.1 -p 5431 -U postgres -d postgres -c 'create database swapi'