# Advanced SQL Material Prep

This repo contains the material for generating
data for the Advanced SQL class

To generate one week of data it takes approx:
 - 25 minutes
 - 120 MB disk
 - ? MB of memory
 - 100% CPU


To build one year:

- 22 hours
- 6 GB Disk

docker run --name pdl -p 5555:5432 -d postgres:latest
python main.py -v "postgresql://postgres@localhost:5555"
