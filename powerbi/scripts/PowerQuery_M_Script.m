// ==============================================================================
// INDIA AIR QUALITY ANALYSIS - POWER QUERY (M) SCRIPTS
// ==============================================================================
// Instructions:
// 1. Open Power BI Desktop.
// 2. Click Home -> Transform Data to open Power Query Editor.
// 3. Under Parameters, create a parameter named "DataFolderPath" pointing to your
//    powerbi/data folder (e.g., "C:\Users\username\Desktop\Air\powerbi\data" or relative path).
// 4. Create blank queries for each table below and paste the respective M block.
// ==============================================================================

// ------------------------------------------------------------------------------
// TABLE 1: Dim_City
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\Dim_City.csv"),[Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"City_Key", Int64.Type},
        {"City", type text},
        {"State", type text},
        {"Region", type text},
        {"Latitude", type number},
        {"Longitude", type number},
        {"Is_Metropolitan", Int64.Type}
    })
in
    #"Changed Type"


// ------------------------------------------------------------------------------
// TABLE 2: Dim_Date
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\Dim_Date.csv"),[Delimiter=",", Columns=15, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"Date", type date},
        {"Year", Int64.Type},
        {"Quarter", Int64.Type},
        {"Quarter_Name", type text},
        {"Month", Int64.Type},
        {"Month_Name", type text},
        {"Month_Short", type text},
        {"Year_Month", type text},
        {"Day", Int64.Type},
        {"Day_Of_Week", type text},
        {"Day_Of_Week_Number", Int64.Type},
        {"Is_Weekend", Int64.Type},
        {"Season", type text},
        {"Lockdown_Phase", type text},
        {"Is_Lockdown", Int64.Type}
    })
in
    #"Changed Type"


// ------------------------------------------------------------------------------
// TABLE 3: Dim_AQI_Category
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\Dim_AQI_Category.csv"),[Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"Category_Key", Int64.Type},
        {"Category_Name", type text},
        {"AQI_Min", Int64.Type},
        {"AQI_Max", Int64.Type},
        {"Color_Hex", type text},
        {"Health_Impact", type text}
    })
in
    #"Changed Type"


// ------------------------------------------------------------------------------
// TABLE 4: Dim_Pollutant
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\Dim_Pollutant.csv"),[Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"Pollutant_Code", type text},
        {"Pollutant_Name", type text},
        {"Unit", type text},
        {"CPCB_Limit_24hr", type number},
        {"WHO_Limit_24hr", type number},
        {"Primary_Sources", type text}
    })
in
    #"Changed Type"


// ------------------------------------------------------------------------------
// TABLE 5: Fact_Daily_Readings
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\Fact_Daily_Readings.csv"),[Delimiter=",", Columns=27, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"Reading_ID", Int64.Type},
        {"Date", type date},
        {"City", type text},
        {"State", type text},
        {"Region", type text},
        {"PM2.5", type number},
        {"PM10", type number},
        {"NO", type number},
        {"NO2", type number},
        {"NOx", type number},
        {"NH3", type number},
        {"CO", type number},
        {"SO2", type number},
        {"O3", type number},
        {"Benzene", type number},
        {"Toluene", type number},
        {"AQI", type number},
        {"AQI_Category", type text},
        {"PM25_PM10_Ratio", type number},
        {"NAAQS_Exceed", Int64.Type},
        {"WHO_Exceed", Int64.Type},
        {"Rolling_7Day_AQI", type number},
        {"Rolling_30Day_AQI", type number},
        {"Lockdown_Flag", Int64.Type},
        {"Lockdown_Phase", type text},
        {"Dominant_Pollutant", type text},
        {"City_Year_Rank", Int64.Type}
    })
in
    #"Changed Type"


// ------------------------------------------------------------------------------
// TABLE 6: Fact_Lockdown_Impact
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "\Fact_Lockdown_Impact.csv"),[Delimiter=",", Columns=14, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"City", type text},
        {"State", type text},
        {"Region", type text},
        {"Pre_Lockdown_AQI", type number},
        {"Lockdown_AQI", type number},
        {"Post_Lockdown_AQI", type number},
        {"AQI_Drop_Points", type number},
        {"Pct_AQI_Reduction", type number},
        {"Pre_Lockdown_PM25", type number},
        {"Lockdown_PM25", type number},
        {"Pct_PM25_Drop", type number},
        {"Pre_Lockdown_NO2", type number},
        {"Lockdown_NO2", type number},
        {"Pct_NO2_Drop", type number}
    })
in
    #"Changed Type"
