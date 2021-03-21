# Advanced SQL Material Prep

VM Setup Guide: https://docs.google.com/document/d/1vbKJdXfwSeCbhZwaRg_t97D62tR6MSqMiEl5NuvCky4

This repo contains the material for generating
data for the Advanced SQL class

To generate one week of data it takes approx:
 - ~60 minutes
 - 120 MB disk
 - ? MB of memory
 - 100% CPU

To build one year:

- 22 hours
- 6 GB Disk

#### To Build For Class

```
make build

# To push to docker hub...
make push
```

Then use the VM configuration guide and the config.sh script on the VM to ready the machine for class.
