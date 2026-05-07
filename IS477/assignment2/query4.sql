SELECT
    Airline AS Airline,
    FlightNumber AS FlightNumber
FROM
    Airport3_Arrivals
WHERE
    Scheduled != Actual;