#!/bin/bash
sleep 1
flask db upgrade
python app.py