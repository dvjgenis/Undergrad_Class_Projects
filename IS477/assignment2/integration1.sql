INSERT OR IGNORE INTO Integrated_Arrival (
    Airline,
    FlightNumber,
    ScheduledArrivalDate,
    ActualArrivalDate,
    ScheduledArrivalTime,
    ActualArrivalTime,
    GateTime,
    LandingTime,
    ArrivalGate
)
SELECT
    'A1' AS Airline,
    s.FlightNumber AS FlightNumber,
    f.ArrivalDate AS ScheduledArrivalDate,
    f.ArrivalDate AS ActualArrivalDate,
    s.ArrivalTime AS ScheduledArrivalTime,
    f.ArrivalTime AS ActualArrivalTime,
    a.GateTime AS GateTime,
    a.LandingTime AS LandingTime,
    f.ArrivalGate AS ArrivalGate
FROM
    Airline1_Flight f
JOIN
    Airline1_Schedule s ON f.FlightId = s.FlightId
LEFT JOIN
    Airport3_Arrivals a ON a.FlightNumber = s.FlightNumber
    AND a.Airline = 'A1'
    AND a.Scheduled = f.ArrivalDate;