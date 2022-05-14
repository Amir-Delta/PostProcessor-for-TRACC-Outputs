# This script extracts TRACC outputs from a Microsoft SQL Server database and performs some postprocessing steps on them
# The output of the script would be a csv file with accessibility score calcultaed for each unit of analysis (here, each US Census Block)

# Importing the packages
import os 
import pandas as pd
import numpy as np
import pyodbc
import sqlite3
import sqlalchemy

# ---------------------Assigning Database/Output Variables:----------------------------------- 
Server='Server-Name' # The name of the Microsoft SQL server in which the TRACC results are saved
Database='Database-Name' # The name of the Microsoft SQL database in which the TRACC results are saved
ResultHeaderId=1 # An integer that relates to a specific TRACC run.
output='path\\AccessibiltyScore.csv' # Specify the path and name of the output csv file. This csv file will contain calculated accessibility score for each unit of analysis

# ---------------------Assigning Accessibility Function Parameters:-----------------------------------
# These parameters are based on the points of interest categories and assumption defined in the study titled "Developing a Census Block Level Accessibility Measure for St. Louis Metropolitan Area" by Poorfakhraei et. al (2019).
# These parameters can be changed based on your own assumptions and points of interest categories.

# Assigning Saturation and Weight for points of interest categories
Edu_Saturation, Edu_Weight= 20, 0.6 
Entrtn_Saturation, Entrtn_Weight= 20, 0.5 
Food_Saturation, Food_Weight= 100, 0.1 
Grocry_Saturation, Grocry_Weight= 10, 3.0 
Hosp_Saturation, Hosp_Weight= 1, 6.0 
Pharma_Saturation, Pharma_Weight= 10, 0.6
Public_Saturation, Public_Weight= 40, 0.4
Shop_Saturation, Shop_Weight= 100, 0.1

# Assigning the travel time catchment (in minutes)
threshold_minutes= 30

# Assigning beta parameter
beta=0.01
# ---------------------------------------------------------------------------------

# Defining a function that extracts TRACC outputs from the Microsoft SQL Server database, merges them, and saves the merged data into a SQLite database
def SQLServerToSQLite(Server,Database,ResultHeaderId):
    # Craeting the connection to the restored database
    con = pyodbc.connect(Driver='{SQL Server}',
                          Server=Server,
                          Database=Database,
                          Trusted_Connection='yes')
    # Reading all the origins and converting them into a dataframe
    sql='SELECT OriginID, Name, XCoord, YCoord FROM Origin'
    origins= pd.read_sql(sql,con)
    origins.columns=["OrigID","OrigName","OrigXCoord","OrigYCoord"]
    # Reading all the destinations and converting them into a dataframe
    sql='SELECT DestinationID, Description, XCoord, YCoord FROM Destination'
    destinations= pd.read_sql(sql,con)
    destinations.columns=["DestID","Category","DestXCoord","DestYCoord"]
    # Reading the results
    sql='SELECT OriginID, DestinationID, TotalJourneyDistance, TotalJourneyTime FROM Result where ResultHeaderId='+str(ResultHeaderId)
    travelTime= pd.read_sql(sql,con)
    # Closing the connection
    con.close()
    # Merging the results with the origins, and destinations
    travelTime=travelTime.merge(origins, left_on='OriginID', right_on='OrigID', how='inner') 
    travelTime=travelTime.merge(destinations, left_on='DestinationID', right_on='DestID', how='inner') 
    # Selecting only the relevant fields of the results (to save memory) and saving them toa local sqlite db
    travelTime=travelTime[["OrigName", "Category", "TotalJourneyDistance", "TotalJourneyTime"]]
    # Creating a SQLAlchemy engine and using it to save data into a sqlite database
    engine = sqlalchemy.create_engine('sqlite:///Results.db')
    travelTime.to_sql(name="Results", con=engine, if_exists = 'append', index=False)
    engine.dispose()
    
# Running the above defined function
SQLServerToSQLite(Server,Database,ResultHeaderId)

# Connecting to the SQLite database that the merged data was saved in
conn=sqlite3.connect("Results.db") 

# Selecting transit trips where the travel time is under 2 miles and naming it data
query = "select * from Results where TotalJourneyTime <= '%s'" % threshold_minutes
data=pd.read_sql(query, conn)

# Creating a new column named dist_factored where the value is an exponential factor of distance. This will be a value accounting for distance deterrioration
data['dist_factored']=np.exp(-beta*data['TotalJourneyTime']).round(2)

# Assigning the weights to each row of the data based on the POI category
data.loc[data['Category'] == 'Education' ,'Weight']=Edu_Weight
data.loc[data['Category'] == 'Entertainment and Recreation' ,'Weight']=Entrtn_Weight
data.loc[data['Category'] == 'Food and Drink' ,'Weight']=Food_Weight
data.loc[data['Category'] == 'Grocery Stores' ,'Weight']=Grocry_Weight
data.loc[data['Category'] == 'Hospitals' ,'Weight']=Hosp_Weight
data.loc[data['Category'] == 'Pharmacies' ,'Weight']=Pharma_Weight
data.loc[data['Category'] == 'Public Services and Banks' ,'Weight']=Public_Weight
data.loc[data['Category'] == 'Shopping' ,'Weight']=Shop_Weight

# Calculating scores for each POI (row) based on the deterrence factor and the weights 
data['score']=data['dist_factored']*data['Weight']

# Summing he N closest POI in each category for each census block (N is the target number for the POI category)
grouped=pd.concat([
data.query('Category == "Education"').groupby(['OrigName','Category'])['score'].nlargest(Edu_Saturation).sum(level=[0,1]),
data.query('Category == "Entertainment and Recreation"').groupby(['OrigName','Category'])['score'].nlargest(Entrtn_Saturation).sum(level=[0,1]),
data.query('Category == "Food and Drink"').groupby(['OrigName','Category'])['score'].nlargest(Food_Saturation).sum(level=[0,1]),
data.query('Category == "Grocery Stores"').groupby(['OrigName','Category'])['score'].nlargest(Grocry_Saturation).sum(level=[0,1]),
data.query('Category == "Hospitals"').groupby(['OrigName','Category'])['score'].nlargest(Hosp_Saturation).sum(level=[0,1]),
data.query('Category == "Pharmacies"').groupby(['OrigName','Category'])['score'].nlargest(Pharma_Saturation).sum(level=[0,1]),
data.query('Category == "Public Services and Banks"').groupby(['OrigName','Category'])['score'].nlargest(Public_Saturation).sum(level=[0,1]),
data.query('Category == "Shopping"').groupby(['OrigName','Category'])['score'].nlargest(Shop_Saturation).sum(level=[0,1])
])

# Summing the scores in each category to come up with the total score in each census block and naming it final_score
final_score=grouped.groupby('OrigName').sum()

# Converting the final score to a table (dataframe) and saving it to the output file
pd.DataFrame(final_score).to_csv(output)
conn.close()

# Deleting the SQLite database
os.remove("Results.db")
