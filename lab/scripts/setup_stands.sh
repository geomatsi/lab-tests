#!/bin/bash

labgrid-client -p test1 create
labgrid-client -p test1 add-match 'webb/slot1/*'

labgrid-client -p test2 create
labgrid-client -p test2 add-match 'webb/slot2/*'
