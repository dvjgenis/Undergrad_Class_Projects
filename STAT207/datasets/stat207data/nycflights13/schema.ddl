create table airlines
(
    carrier text primary key,
    name text
);

create table airports
(
    faa text primary key,
    name text,
    lat integer,
    lon integer,
    alt integer,
    tz integer,
    dst text,
    tzone text
);

create table planes
(
    tailnum text primary key,
    year integer,
    type text,
    manufacturer text,
    model text,
    engines integer,
    seats integer,
    speed text,
    engine text
);

create table weather
(
    origin text,
    year integer,
    month integer,
    day integer,
    hour integer,
    temp integer,
    dewp integer,
    humid integer,
    wind_dir integer,
    wind_speed integer,
    wind_gust integer,
    precip integer,
    pressure integer,
    visib integer,
    time_hour text
);

create table flights (
    year integer,
    month integer,
    day integer,
    dep_time integer,
    sched_dep_time integer,
    dep_delay integer,
    arr_time integer,
    sched_arr_time integer,
    arr_delay integer,
    carrier text,
    flight text,
    tailnum text,
    origin text,
    dest text,
    air_time integer,
    distance integer,
    hour integer,
    minuteinteger ,
    time_hour text,
    FOREIGN KEY(carrier) REFERENCES airline(carrier)
    FOREIGN KEY(tailnum) REFERENCES planes(tailnum)    
)