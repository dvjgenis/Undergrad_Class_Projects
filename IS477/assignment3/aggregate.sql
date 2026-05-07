.mode csv
.headers on
.output results/sql-fac-types.csv
SELECT Facility_Type, COUNT(*) AS Count
FROM Inspections
GROUP BY Facility_Type
ORDER BY Facility_Type ASC;