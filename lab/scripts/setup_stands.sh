#!/bin/bash

for i in `seq 1 8`; do
	labgrid-client -p slot$i create
	labgrid-client -p slot$i add-match "webb/slot$i/*"
done
