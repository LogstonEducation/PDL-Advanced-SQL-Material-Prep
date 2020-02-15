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
