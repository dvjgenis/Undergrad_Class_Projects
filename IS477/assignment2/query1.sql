SELECT
    s.FlightNumber AS FlightNumber,
    s.ArrivalAirport AS ArrivalAirport,
    f.ArrivalGate AS ArrivalGate
FROM
    Airline1_Flight f
JOIN
    Airline1_Schedule s ON f.FlightId = s.FlightId;