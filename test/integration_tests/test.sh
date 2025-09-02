#!/bin/bash

shopt -s expand_aliases 
echo "This script, and other scripts here are meant to be ran in the project root. ie. Not the src or test folders, but the parent folder of those scripts"
alias qstat="python ./test/integration_tests/mocks/mock_qstat.py"
alias xqstat="python ./test/integration_tests/mocks/mock_xqstat.py"

python ./src/automagician.py

unalias qstat
unalias xqstat