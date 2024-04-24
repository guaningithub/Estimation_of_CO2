/**--drop table NewTable;
CREATE TABLE NewTable (
    YearMonth varchar(200),
    lat float,
    lon float,
    AvgXCO2 float,
    ndvi float,
    NightLight float
)

INSERT INTO NewTable (YearMonth, lat, lon, AvgXCO2, ndvi, NightLight)
SELECT t1.YearMonth, t1.lat, t1.lon, ROUND(t1.AvgXCO2,2), t2.ndvi, t3.NightLight
FROM MonthlyData_XCO2 t1
JOIN NDVI t2 ON t1.YearMonth = t2.YearMonth AND t1.lat = t2.lat AND t1.lon = t2.lon
JOIN NightLight t3 ON t1.YearMonth = t3.YearMonth AND t1.lat = t3.lat AND t1.lon = t3.lon
WHERE t1.AvgXCO2 IS NOT NULL AND t2.ndvi IS NOT NULL AND t3.NightLight IS NOT NULL
**/



drop table MATCHINGDATA;
CREATE TABLE MATCHINGDATA (
    YearMonth varchar(20),
    lat float,
    lon float,
    AvgXCO2 float,
    ndvi float,
    NightLight float,
    windu float,
    windv float,
    pres float,
    temp float,
    blh float,
    relh float
)

INSERT INTO MATCHINGDATA (YearMonth, lat, lon, AvgXCO2, ndvi, NightLight, windu, windv, pres, temp, blh, relh)
SELECT t1.YearMonth, t1.lat, t1.lon, ROUND(t1.AvgXCO2, 2), ROUND(t2.ndvi,2), ROUND(t3.NightLight,2), ROUND(t4.windu,2), ROUND(t5.windv,2), ROUND(t6.pres,2), ROUND(t7.temp,2), ROUND(t8.blh,2), ROUND(t9.relh,2)
FROM MonthlyData_XCO2 t1
JOIN NEWNDVI t2 ON t1.YearMonth = t2.YearMonth AND t1.lat = t2.lat AND t1.lon = t2.lon
JOIN NightLight t3 ON t1.YearMonth = t3.YearMonth AND t1.lat = t3.lat AND t1.lon = t3.lon
JOIN windu_monthly t4 ON t1.YearMonth = t4.YearMonth AND t1.lat = t4.lat AND t1.lon = t4.lon
JOIN windv_monthly t5 ON t1.YearMonth = t5.YearMonth AND t1.lat = t5.lat AND t1.lon = t5.lon
JOIN pres_monthly t6 ON t1.YearMonth = t6.YearMonth AND t1.lat = t6.lat AND t1.lon = t6.lon
JOIN temp_monthly t7 ON t1.YearMonth = t7.YearMonth AND t1.lat = t7.lat AND t1.lon = t7.lon
JOIN blh_monthly t8 ON t1.YearMonth = t8.YearMonth AND t1.lat = t8.lat AND t1.lon = t8.lon
JOIN relh_monthly t9 ON t1.YearMonth = t9.YearMonth AND t1.lat = t9.lat AND t1.lon = t9.lon
WHERE t1.AvgXCO2 IS NOT NULL AND t2.ndvi IS NOT NULL AND t3.NightLight IS NOT NULL AND t4.windu IS NOT NULL AND t5.windv IS NOT NULL AND t6.pres IS NOT NULL AND t7.temp IS NOT NULL AND t8.blh IS NOT NULL AND t9.relh IS NOT NULL 
