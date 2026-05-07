DROP TABLE IF EXISTS Inspections;

create table Inspections (
   Inspection_ID NUMBER,
   DBA_Name TEXT,
   AKA_Name TEXT,
   License_Num NUMBER,
   Facility_Type TEXT,
   Risk TEXT,
   Address TEXT,
   City TEXT,
   State TEXT,
   Zip NUMBER,
   Inspection_Date TEXT,
   Inspection_Type TEXT,
   Results TEXT,
   Violations TEXT,
   Latitude NUMBER,
   Longitude NUMBER,
   Location TEXT,
   PRIMARY KEY (Inspection_ID)
); 


.mode csv
.import --skip 1 input/Food_Inspections_50k.csv Inspections
