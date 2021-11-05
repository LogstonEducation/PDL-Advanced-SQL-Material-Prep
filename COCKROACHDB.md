# CockroachDB Setup

This guide walks you through the steps of setting up a CockroachDB Free-Tier
database and loading the "airline" DB into that database.

1. Once you have created your VM, dump the data from the running postgres
   database:

    ```
    pg_dump -U postgres -h localhost -d airline --no-owner --no-comments > airline.sql
    ```

1. Create an account at https://cockroachlabs.cloud/. Then if you haven't
   already, create a free Serverless cluster. After you create your cluster you
   will be shown a "Connection Info" modal with means of connecting your
   cluster based on OS. If you are on a linux (eg. Debian, Ubuntu) machine,
   ensure you've changed "Choose your OS" to linux. Copy and run all three
   steps listed to ensure you can connect to the cluster.

1. Once you know you can connect to your cluster, navigate back to
   Cockroachlabs.cloud and to the "SQL users" page for your cluster. Change the
   password for you SQL user to something memorable so it can be used
   throughout this guide.

1. Click the connect button again and copy the connection string in the last
   step of the connect guide. It should look like the following:

    ```
    cockroach sql --url 'postgresql://paul:<ENTER-PASSWORD>@free-tier4.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&sslrootcert='$HOME'/.postgresql/root.crt&options=--cluster%3Dpdl-advanced-sql-924'
    ```

1. Find your **DSN**, ie the part after "--url" Eg
   `'postgres://paul:<ENTER..>@free-tie...sql-924'` Make sure to insert your
   password (ie. the `<ENTER-PASSWORD>` after the username `paul`) or the DSN
   will not work with the following commands. Strip the SSL and cert query
   parameters from the DSN...

    ```
    'postgresql://paul:abc123@free-tier4.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&sslrootcert='$HOME'/.postgresql/root.crt&options=--cluster%3Dpdl-advanced-sql-924'
    ```

1. Create the airline database.

    ```
    psql 'postgresql://paul:abc123@free-tier4.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&sslrootcert='$HOME'/.postgresql/root.crt&options=--cluster%3Dpdl-advanced-sql-924'   -c "CREATE DATABASE airline;"
    ```

1. Change the name of the database in the URL to `airline` and pipe the
   airline.sql file into the db:

    ```
    psql 'postgresql://paul:abc123@free-tier4.aws-us-west-2.cockroachlabs.cloud:26257/airline?sslmode=verify-full&sslrootcert='$HOME'/.postgresql/root.crt&options=--cluster%3Dpdl-advanced-sql-924' < airline.sql
    ```
    
    There will be a lot of errrors but you can ignore them all.

1. Finally, connect with pgcli:

    ```
    pgcli 'postgresql://paul:abc123@free-tier4.aws-us-west-2.cockroachlabs.cloud:26257/airline?sslmode=verify-full&sslrootcert='$HOME'/.postgresql/root.crt&options=--cluster%3Dpdl-advanced-sql-924'
    ```
