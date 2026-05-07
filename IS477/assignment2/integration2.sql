INSERT INTO Integrated_Arrival (
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
    'A2' AS Airline,
    f.FlightNumber AS FlightNumber,
    f.ScheduledArrivalDate AS ScheduledArrivalDate,
    CASE
        WHEN a.Actual IS NOT NULL THEN a.Actual
        ELSE f.ScheduledArrivalDate
    END AS ActualArrivalDate,
    f.ScheduledArrivalTime AS ScheduledArrivalTime,
    f.ActualArrivalTime AS ActualArrivalTime,
    a.GateTime AS GateTime,
    a.LandingTime AS LandingTime,
    CASE
        WHEN a.Terminal IS NOT NULL AND a.Gate IS NOT NULL THEN a.Terminal || a.Gate
        ELSE NULL
    END AS ArrivalGate
FROM
    Airline2_Flight f
LEFT JOIN
    Airport3_Arrivals a ON a.FlightNumber = f.FlightNumber
    AND a.Airline = 'A2'
    AND a.Scheduled = f.ScheduledArrivalDate;