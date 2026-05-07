create table Airline1_Schedule(
    FlightId NUMBER,
    FlightNumber NUMBER,
    StartDate TEXT,
    EndDate TEXT,
    DepartureTime TEXT,
    DepartureAirport TEXT,
    ArrivalTime TEXT,
    ArrivalAirport TEXT,
    PRIMARY KEY (FlightId)
) ;

create table Airline1_Flight(
    FlightId NUMBER,
    DepartureDate TEXT,
    DepartureTime TEXT, 
    DepartureGate TEXT,
    ArrivalDate TEXT,
    ArrivalTime TEXT,
    ArrivalGate TEXT,
    PlaneId NUMBER,
    PRIMARY KEY (FlightId, DepartureDate),
    FOREIGN KEY (FlightId) REFERENCES Airline1_Schedule(FlightId)    
) ;

create table Airline2_Flight (
    FlightNumber NUMBER,
    DepartureAirport TEXT,
    ScheduledDepartureDate TEXT,
    ScheduledDepartureTime TEXT,
    ActualDepartureTime TEXT,
    ArrivalAirport TEXT,
    ScheduledArrivalDate TEXT,
    ScheduledArrivalTime TEXT,
    ActualArrivalTime TEXT,
    PRIMARY KEY (FlightNumber, DepartureAirport, ScheduledDepartureDate)
);

create table Airport3_Arrivals (
    Airline TEXT,
    FlightNumber NUMBER,
    Scheduled TEXT,
    Actual TEXT,
    GateTime TEXT,
    LandingTime TEXT,
    Terminal TEXT,
    Gate TEXT,
    Runway TEXT,
    PRIMARY KEY (Airline, FlightNumber, Scheduled)
) ;

create table Airport3_Departures (
    Airline TEXT,
    FlightNumber NUMBER,
    Scheduled TEXT,
    Actual TEXT,
    GateTime TEXT,
    TakeoffTime TEXT,
    Terminal TEXT,
    Gate TEXT,
    Runway TEXT,
    PRIMARY KEY (Airline, FlightNumber, Scheduled)
) ;

create table Airfare4_Fares (
    FlightId NUMBER,
    FareClass TEXT,
    Fare NUMBER,
    PRIMARY KEY (FlightId, FareClass)
);

create table Airfare4_Flight (
    FlightId NUMBER,
    FlightNumber TEXT,
    DepartureAirport TEXT,
    DepartureDate TEXT,
    DepartureTime TEXT,
    ArrivalAirport TEXT,
    ArrivalTime TEXT,
    PRIMARY KEY (FlightId)
) ;

create table Airinfo5_AirlineCodes (
    AirlineCode TEXT,
    AirlineName TEXT,
    PRIMARY KEY (AirlineCode)
) ;

create table Airinfo5_AirportCodes (
    AirportCode TEXT,
    AirportName TEXT,
    PRIMARY KEY (AirportCode)
) ;