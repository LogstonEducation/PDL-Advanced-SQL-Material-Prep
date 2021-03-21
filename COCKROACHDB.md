# CockroachDB Setup

This guide walks you throught the steps of setting up a CockroachDB Free-Tier database and loading the "airline" DB into that database.

1. On you already create VM, dump the data from the running postgres database:

    ```
    pg_dump -U postgres -h localhost -d airline --no-owner --no-comments > airline.sql
    ```

1. Create an account at https://cockroachlabs.cloud/. Then create a Free-Tier database and make a note of the "Connect Info" after creation is complete. Copy your "connect info" right after creating a free tier database:

    ```
    cockroach sql --url 'postgres://paul@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/airline?sslmode=verify-full&sslrootcert=<your_certs_directory>/cc-    ca.crt&options=--cluster=sturdy-gopher-1409'
    ```

1. Find your **DSN**, ie the part after "--url" Eg `'postgres://paul:abc123def@free-tie...gopher-1409'` Make sure your password is included (ie. the `abc123def` after the username `paul`) or the DSN will not work with the following commands. Strip the SSL and cert query parameters from the DSN...

    ```
    'postgres://paul:abc123def@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/defaultdb?options=--cluster=sturdy-gopher-1409'
    ```

1. Replace the last "=" sign with "%3D"...

    ```
    'postgres://paul:abc123def@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/defaultdb?options=--cluster%3Dsturdy-gopher-1409'
    ```

1. Create the airline database.

    ```
    psql 'postgres://paul:abc123def@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/defaultdb?options=--cluster%3Dsturdy-gopher-1409'  -c "CREATE DATABASE airline;"
    ```

1. Change the name of the database in the URL to airline and pipe the airline.sql file into the db:

    ```
    psql 'postgres://paul:abc123def@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/airline?options=--cluster%3Dsturdy-gopher-1409'  < airline.sql
    ```
    
    There will be a lot of errrors but you can ignore them all.

1. Finally, connect with pgcli:

    ```
    pgcli 'postgres://paul:abc123def@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/airline?options=--cluster%3Dsturdy-gopher-1409'
    ```
