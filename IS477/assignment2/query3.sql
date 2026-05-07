SELECT
    Airline AS Airline,
    FlightNumber AS FlightNumber,
    'EWR' AS ArrivalAirport,
    Terminal || Gate AS ArrivalGate
FROM
    Airport3_Arrivals;