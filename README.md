# Advanced SQL Material Prep

VM Setup Guide: https://docs.google.com/document/d/1vbKJdXfwSeCbhZwaRg_t97D62tR6MSqMiEl5NuvCky4

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

#### To Build For Class

```
make build
make gzip
```

#### To Run

./reset-db.sh
python main.py -v "postgresql://postgres@localhost:5555"

