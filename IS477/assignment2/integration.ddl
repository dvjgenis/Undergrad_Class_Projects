CREATE TABLE Integrated_Arrival (
    Airline TEXT,
    FlightNumber NUMBER,
    ScheduledArrivalDate TEXT,
    ActualArrivalDate TEXT,
    ScheduledArrivalTime TEXT,
    ActualArrivalTime TEXT,
    GateTime TEXT,
    LandingTime TEXT,
    ArrivalGate TEXT,
    PRIMARY KEY (Airline, FlightNumber, ScheduledArrivalDate)
);