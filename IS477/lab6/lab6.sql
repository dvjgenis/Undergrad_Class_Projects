INSERT INTO Lab6_Flights
SELECT 'A1' as Airline, s.FlightNum, s.DepartureAirport,
       f.DepartureDate, s.DepartureTime, f.DepartureTime,
       s.ArrivalAirport, f.ArrivalDate, s.ArrivalTime, 
       f.ArrivalTime
FROM Airline1_Schedule as s, Airline1_Flight as f
WHERE s.FlightId = f.FlightId ;

INSERT INTO Lab6_Flights  
SELECT 'A2' as Airline, f.FlightNumber, f.DepartureAirport, f.ScheduledDepartureDate, 
    f.ScheduledDepartureTime, f.ActualDepartureTime,
    f.ArrivalAirport, f.ScheduledArrivalDate, f.ScheduledArrivalTime,
    f.ActualArrivalTime
FROM Airline2_Flight as f ;