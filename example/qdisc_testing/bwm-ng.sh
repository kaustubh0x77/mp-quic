#!/bin/bash

flags=(
    -o csv
    -F results.csv         # Name of output csv file
    -C ","              # CSV delimiter
    -u bytes            # Units: 'bytes', 'bits', 'packets', 'errors'
    -T rate     
    -c 5                # Number of outputs
    -t 2000             # Time interval between consecutive reading
    
    # List of interfaces to inspect
    -I s1-eth1,s2-eth1  
)

bwm-ng "${flags[@]}"