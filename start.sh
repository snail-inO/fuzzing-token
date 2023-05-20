#!/bin/bash

while read line; do
    python3 scripts/test_token.py $line
done < candidate_list.txt
