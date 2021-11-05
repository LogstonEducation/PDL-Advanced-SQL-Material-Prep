##### How many flights in 2020?

```
SELECT count(*)
FROM route_flights
WHERE start_ts >= '2020-01-01'
  AND start_ts < '2021-01-01'
```

##### How many flights in the past year?

```
SELECT count(*)
FROM route_flights
WHERE start_ts <= now()
  AND start_ts > now() - INTERVAL '1 year'
```

### Subqueries and Joins!

##### What are the highest and lowest mile counts (ie. Tach Time)?

```
SELECT max(tach_time) as tach_time
FROM aircraft

UNION

SELECT min(tach_time) as tach_time
FROM aircraft;
```

##### What aircraft have the most miles, least? Together?

```
SELECT a.id, a.tach_time
FROM aircraft a
WHERE a.tach_time in (
    SELECT max(tach_time) as tach_time
    FROM aircraft
    UNION
    SELECT min(tach_time) as tach_time
    FROM aircraft
);
```

##### How many times has each FF# been used?

```
SELECT p.frequent_flyer_number, count(p.id)
FROM passengers p
WHERE p.frequent_flyer_number IS NOT NULL
GROUP BY p.frequent_flyer_number
ORDER BY count(p.id) DESC;
```


##### What passengers have flown the most (what if they have very similar names but not quite the same)? Doe these number agree with the FF numbers from above?

```
SELECT
    p.first_name,
    p.last_name,
    count(p.id)
FROM passengers p
GROUP BY p.first_name, p.last_name
HAVING count(p.id) > 1
ORDER BY count(p.id) DESC;
```

##### How many passengers have the same name?

```
SELECT *
FROM passengers p1, passengers p2
WHERE p1.first_name = p2.first_name
  AND p1.last_name = p2.last_name
  AND p1.id < p2.id;
```

##### What Origin Destination combo sells the most?

  - Thought plan:
      - I need the table with route information
      - For each route, I need a count of flights
      - For each flight, I need the number of seats sold
      - Order that by most to least

```
SELECT origin_code, destination_code, count(sa.id)
FROM routes r
LEFT JOIN route_flights rf ON r.id = rf.route_id
LEFT JOIN seat_assignments sa ON rf.id = sa.route_flight_id
GROUP BY origin_code, destination_code
ORDER BY count(sa.id) DESC;
```

Why not join on ticket table? Loads another unneeded table. Seat assignment is one to one with ticket and all we need is a count of tickets.

##### What is the most sold seat?

```
SELECT count(sa.id), acs.number
FROM seat_assignments sa
LEFT JOIN aircraft_seat acs ON acs.id = sa.seat_id
GROUP BY acs.number
ORDER BY count(sa.id) DESC;
```

##### What is the most unsold seat?

Can we use the least frequently sold seat? Some seats may never get sold.
Would it show up in our previous query? NO. Left join would not include
"empty" results form aircraft_seat.

Can we flip the JOIN? YEP.

```
SELECT acs.number, count(sa.id)
FROM aircraft_seat acs
LEFT JOIN seat_assignments sa ON acs.id = sa.seat_id
GROUP BY acs.number
ORDER BY count(sa.id) ASC;
```

BUT....

What is this question even asking? A40 on one plane is not A40 on another plane,
because other planes may not even have A40. We really need to know what
the seat's "context" is. Ie. Where on the plan is least sold? This is going to
be specific aircraft type, seat class, etc.

```
SELECT at.manufacturer, at.model, acs.number, count(sa.seat_id)
FROM tickets t
LEFT JOIN seat_assignments sa ON t.seat_assignment_id = sa.id
LEFT JOIN aircraft_seat acs ON sa.seat_id = acs.id
LEFT JOIN aircraft_types at ON acs.aircraft_type_id = at.id
GROUP BY at.manufacturer, at.model, acs.number;
```

```
SELECT at.manufacturer, at.model, acs.number, acs.type, acs.location, count(sa.seat_id)
FROM tickets t
LEFT JOIN seat_assignments sa ON t.seat_assignment_id = sa.id
LEFT JOIN aircraft_seat acs ON sa.seat_id = acs.id
LEFT JOIN aircraft_types at ON acs.aircraft_type_id = at.id
GROUP BY at.manufacturer, at.model, acs.number, acs.type, acs.location
ORDER BY count(sa.seat_id);
```

##### What is the most unsold Orig -> Dest

Let start by by looking at seat assignment records for a route flight...
This give us the number of seats sold per route flight

```
SELECT sa.route_flight_id, count(sa.id)
FROM seat_assignments sa
GROUP BY sa.route_flight_id;
```

This gives us the total number of seats on the plane.

```
SELECT count(acs.id) as total
FROM route_flights rf
LEFT JOIN aircraft a ON rf.aircraft_id = a.id
LEFT JOIN aircraft_types at ON a.type_id = at.id
LEFT JOIN aircraft_seat acs ON at.id = acs.aircraft_type_id
WHERE rf.id = 2
GROUP BY rf.id;
```

Can we combine the two? Yep.

```
SELECT
    count(acs.id) as total,
    (SELECT count(id)
     FROM seat_assignments sa
     WHERE rf.id = sa.route_flight_id) as sold
FROM route_flights rf
LEFT JOIN aircraft a ON rf.aircraft_id = a.id
LEFT JOIN aircraft_types at ON a.type_id = at.id
LEFT JOIN aircraft_seat acs ON at.id = acs.aircraft_type_id
WHERE rf.id = 2
GROUP BY rf.id;
```

Can we get a percentage?

```
SELECT
    div(
     (SELECT count(id)
      FROM seat_assignments sa
      WHERE rf.id = sa.route_flight_id),
     count(acs.id)
    )
FROM route_flights rf
LEFT JOIN aircraft a ON rf.aircraft_id = a.id
LEFT JOIN aircraft_types at ON a.type_id = at.id
LEFT JOIN aircraft_seat acs ON at.id = acs.aircraft_type_id
WHERE rf.id = 2
GROUP BY rf.id;
```

Why zero?

```
SELECT
    div(
     (SELECT count(id)
      FROM seat_assignments sa
      WHERE rf.id = sa.route_flight_id),
     count(acs.id)
    )
FROM route_flights rf
LEFT JOIN aircraft a ON rf.aircraft_id = a.id
LEFT JOIN aircraft_types at ON a.type_id = at.id
LEFT JOIN aircraft_seat acs ON at.id = acs.aircraft_type_id
WHERE rf.id = 2
GROUP BY rf.id;
```

Hmmm, maybe its doing integer division? In that case, we need to drop the "div" function too.

```
SELECT
     (SELECT count(id)
      FROM seat_assignments sa
      WHERE rf.id = sa.route_flight_id) / count(acs.id)::decimal
FROM route_flights rf
LEFT JOIN aircraft a ON rf.aircraft_id = a.id
LEFT JOIN aircraft_types at ON a.type_id = at.id
LEFT JOIN aircraft_seat acs ON at.id = acs.aircraft_type_id
WHERE rf.id = 2
GROUP BY rf.id;
```

Show EXPLAIN.  Add view with this select?

```
EXPLAIN SELECT
     (SELECT count(id)
      FROM seat_assignments sa
      WHERE rf.id = sa.route_flight_id) / count(acs.id)::decimal
FROM route_flights rf
LEFT JOIN aircraft a ON rf.aircraft_id = a.id
LEFT JOIN aircraft_types at ON a.type_id = at.id
LEFT JOIN aircraft_seat acs ON at.id = acs.aircraft_type_id
WHERE rf.id = 2
GROUP BY rf.id;
```

```
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON) SELECT
     (SELECT count(id)
      FROM seat_assignments sa
      WHERE rf.id = sa.route_flight_id) / count(acs.id)::decimal
FROM route_flights rf
LEFT JOIN aircraft a ON rf.aircraft_id = a.id
LEFT JOIN aircraft_types at ON a.type_id = at.id
LEFT JOIN aircraft_seat acs ON at.id = acs.aircraft_type_id
WHERE rf.id = 2
GROUP BY rf.id;
```

http://tatiyants.com/pev/#/plans/new
https://thoughtbot.com/blog/reading-an-explain-analyze-query-plan

### Views

Passengers and their meal types

```
SELECT p.last_name, p.first_name, mt.name as meal_type
FROM passengers p
INNER JOIN passenger_preferred_meal_types ppmt ON ppmt.passenger_id = p.id
INNER JOIN meal_types mt ON ppmt.meal_type_id = mt.id
ORDER BY p.last_name, p.first_name, mt.name;
```

```
CREATE VIEW passenger_meal_type AS
SELECT p.last_name, p.first_name, mt.name as meal_type
FROM passengers p
INNER JOIN passenger_preferred_meal_types ppmt ON ppmt.passenger_id = p.id
INNER JOIN meal_types mt ON ppmt.meal_type_id = mt.id
ORDER BY p.last_name, p.first_name, mt.name;
```

- CONS:
  - You can’t insert data into a materialized view as you can with a table.
  - Unless you use REFRESH MATERIALIZED VIEW sales, the data will be stale.
  - You cant create an index on a materialized view
- PROS:
  - They are quick and can clean up code that would otherwise be too complicated to manage.

##### From before...

```
CREATE MATERIALIZED VIEW sales AS SELECT rf.id,
     (SELECT count(id)
      FROM seat_assignments sa
      WHERE rf.id = sa.route_flight_id) / count(acs.id)::decimal as frac_sold
FROM route_flights rf
JOIN aircraft a ON rf.aircraft_id = a.id
JOIN aircraft_types at ON a.type_id = at.id
JOIN aircraft_seat acs ON at.id = acs.aircraft_type_id
GROUP BY rf.id;
```

- CONS:
  - You can’t insert data into a materialized view as you can with a table.
  - Unless you use REFRESH MATERIALIZED VIEW sales, the data will be stale.
- PROS:
  - You can create an index on a materialized view

### Subqueries performance!

Where to put them?

```
EXPLAIN SELECT t3.cost
FROM (
  SELECT cost, (SELECT avg(cost) FROM tickets t2) avg_cost
  FROM tickets t1
) t3
WHERE t3.cost > t3.avg_cost;

                                              QUERY PLAN
------------------------------------------------------------------------------------------------------
 Seq Scan on tickets t1  (cost=16708.08..42308.13 rows=452215 width=8)
   Filter: (cost > $1)
   InitPlan 1 (returns $1)
     ->  Finalize Aggregate  (cost=16708.07..16708.08 rows=1 width=8)
           ->  Gather  (cost=16707.85..16708.06 rows=2 width=32)
                 Workers Planned: 2
                 ->  Partial Aggregate  (cost=15707.85..15707.86 rows=1 width=32)
                       ->  Parallel Seq Scan on tickets t2  (cost=0.00..14294.68 rows=565268 width=8)
```

```
EXPLAIN SELECT t1.cost
FROM tickets t1, (SELECT avg(cost) avg_cost FROM tickets) t2
WHERE t1.cost > t2.avg_cost;

                                           QUERY PLAN
-------------------------------------------------------------------------------------------------
 Nested Loop  (cost=16708.07..55874.58 rows=452215 width=8)
   Join Filter: (t1.cost > (avg(tickets.cost)))
   ->  Finalize Aggregate  (cost=16708.07..16708.08 rows=1 width=8)
         ->  Gather  (cost=16707.85..16708.06 rows=2 width=32)
               Workers Planned: 2
               ->  Partial Aggregate  (cost=15707.85..15707.86 rows=1 width=32)
                     ->  Parallel Seq Scan on tickets  (cost=0.00..14294.68 rows=565268 width=8)
   ->  Seq Scan on tickets t1  (cost=0.00..22208.44 rows=1356644 width=8)
```

```
EXPLAIN SELECT t1.cost
FROM tickets t1
WHERE t1.cost > (SELECT avg(cost) avg_cost FROM tickets);

                                            QUERY PLAN
---------------------------------------------------------------------------------------------------
 Seq Scan on tickets t1  (cost=16708.08..42308.13 rows=452215 width=8)
   Filter: (cost > $1)
   InitPlan 1 (returns $1)
     ->  Finalize Aggregate  (cost=16708.07..16708.08 rows=1 width=8)
           ->  Gather  (cost=16707.85..16708.06 rows=2 width=32)
                 Workers Planned: 2
                 ->  Partial Aggregate  (cost=15707.85..15707.86 rows=1 width=32)
                       ->  Parallel Seq Scan on tickets  (cost=0.00..14294.68 rows=565268 width=8)
```

### CTEs (Common Table Expressions)

```
WITH maxmin AS (
    SELECT max(tach_time) as tach_time
    FROM aircraft
    UNION
    SELECT min(tach_time) as tach_time
    FROM aircraft
)
SELECT a.id, a.tach_time
FROM maxmin mm
LEFT JOIN aircraft a ON mm.tach_time = a.tach_time;
```

CTEs are great! And let you execute a query once and then use the results all over your main query.
However:
 - PostgreSQL (and potentially other DBs) will have trouble moving easy filter params into the CTE.
 - Also, CTEs are materialized in memory. A whole extra table is created on the fly in memory. For
   big tables, this can be very memory consuming.
 - The same indices that you have for your main tables, can not be used on the CTE tables.
   Thus the queries might be very slow.

See https://medium.com/@hakibenita/be-careful-with-cte-in-postgresql-fca5e24d2119 for more details.

### Math Operations

```
SELECT
  abs(-20),
  # if you need to cast a float, you might need more than float. you might need numeric
  round(pi()::numeric, 5),
  ln(exp(1.0)) as ln,
  log(100);
```

```
SELECT
  concat('one', 'two'),
  'one' || 'two',
  trim(' remove spaces '),
  trim(leading '-' from '---510744'),
  lower('HI'),
  upper('hello');
```

LIKE - substr

```
SELECT *
FROM passengers
WHERE first_name LIKE 'Terr%';
```

SIMILAR TO - for regex

```
SELECT *
FROM passengers
WHERE first_name SIMILAR TO 'Kyl(a|e)\s%';
```

regexp_split_to_table

```
SELECT regexp_split_to_table('hi this is so cool', ' ');
```

regexp_split_to_array -- advanced use


### UDFs
```
CREATE [ OR REPLACE ] FUNCTION name ( [ [ argname ] argtype [, ...] ] )
    RETURNS rettype
  { LANGUAGE langname
    | IMMUTABLE | STABLE | VOLATILE
    | CALLED ON NULL INPUT | RETURNS NULL ON NULL INPUT | STRICT
    | [ EXTERNAL ] SECURITY INVOKER | [ EXTERNAL ] SECURITY DEFINER
    | AS 'definition'
    | AS 'obj_file', 'link_symbol'
  } ...
    [ WITH ( attribute [, ...] ) ]
```

```
CREATE OR REPLACE FUNCTION fullname(first_name text, last_name text)
RETURNS text AS
$$
-- variables
DECLARE
  has_newline bool;
-- variables
BEGIN
  RETURN trim(first_name || ' ' || last_name);
END;
$$ LANGUAGE plpgsql;
```

If there is some whitespace that we want to see...

### Transactions

```
SELECT replace(first_name, E'\n', '\n') FROM passengers;
```

Let's replace that...

```
START TRANSACTION; Update passengers SET first_name = replace(first_name, E'\n', '');
```

```
SELECT replace(first_name, E'\n', '\n') FROM passengers;
```

```
COMMIT; -- ROLLBACK;
```

- be sure to rollback if anything goes wrong or else you will forget
- you are in state where nothing can be updated/committed.
- SELECTs should still be okay though.
