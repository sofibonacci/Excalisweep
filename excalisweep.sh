#!/bin/bash

#search and execute test scripts

echo "executing tests wait a minute..."
echo ""
sleep 1
test_dir="tests"
ok_count=0
fail_count=0
#finds every script that ends with "unittest.py"
find "$test_dir" -type f -name "*unittest.py" | while read -r test_file; do
    # Converts file in a module to use with python -m
    module_name=$(echo "$test_file" | sed 's|/|.|g' | sed 's|\.py$||')    
    output=$(python -m unittest "$module_name" 2>&1)
    status=$?
    if [ $status -eq 0 ]; then
        echo "================$test_file: OK================"
        ((ok_count++))
    else
        echo "================$test_file: FAILED================"
        ((fail_count++))   
    fi
    echo ""    
    sleep 1
done

echo "tests done!"
sleep 1 
echo "executing Excalisweep..."
sleep 1
#executing main...
python main.py