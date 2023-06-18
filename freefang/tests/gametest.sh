#!/bin/sh
# Make sure server is running! ../main.py

id=$(python3.10 ./creategame.py)
echo $id

python3.10 ./test.py A $id &
python3.10 ./test.py B $id &
python3.10 ./test.py C $id &
python3.10 ./test.py D $id &
python3.10 ./test.py E $id &
