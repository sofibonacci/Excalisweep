#!/bin/bash

#search and execute test scripts

echo "executing tests, wait a minute..."
sleep 1

python -m unittest discover -s tests -p "*unittest.py"

echo "tests done!"
sleep 1

#execute app
python main.py
