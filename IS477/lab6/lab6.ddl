CREATE TABLE Lab6_Flights(
    Airline TEXT,
    FlightNumber NUMBER,
    DepartureAirport TEXT,
    ScheduledDepartureDate TEXT,
    ScheduledDepartureTime TEXT,
    ActualDepartureTime TEXT,
    ArrivalAirport TEXT,
    ScheduledArrivalDate TEXT,
    ScheduledArrivalTime TEXT,
    ActualArrivalTime TEXT,
    PRIMARY KEY (Airline, FlightNumber, DepartureAirport, ScheduledDepartureDate)
);