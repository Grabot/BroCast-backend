#!/bin/bash
echo "startup backend api"
echo "slight sleep to allow database to setup"
sleep 4
echo "run database commands and then the actual api"
alembic upgrade head
python main.py
