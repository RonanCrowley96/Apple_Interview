# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 15:44:38 2022

@author: Rónán Crowley

Importing Data-set into database and visualise the data

Technologies used:
                    Python
                    Pandas
                    Seaborn
                    mysql.connector
                    Matplotlib
                    MySQL
                    WindroseAxes
                    Numpy


To run, related csv files must be in same directory as .py file

"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector as db  
from windrose import WindroseAxes
from pandas.api.types import CategoricalDtype
import numpy as np


def get_wind_data(yearly_df, year, average_speed_data, l_id):
    
    #Extract all values for wind speed, wind direction and gust for current location id and year.
    ws = yearly_df['WindSpeed'].values       
    wd = yearly_df['WindDirection'].values         
    wg = yearly_df['Gust'].values
    
    #Calculate average speeds rounded to 2 decimal places
    average_wind_speed = np.around(np.average(ws),decimals = 2)
    average_gust_speed = np.around(np.average(wg),decimals = 2)
    
    #Append data to average speed data list
    average_speed_data.append([year,l_id,average_wind_speed,average_gust_speed])
     
    #Return wind related values
    return ws, wd, wg, average_speed_data

def wind_rose(wd, ws, l_id, year):
    
    #Create and show Wind Rose Graph
    ax = WindroseAxes.from_ax()
    ax.bar(wd, ws, normed=True, opening=0.8, edgecolor='white')
    unit = str(l_id) + '_' + str(year)
    filename = 'images\WindRose_' + unit + '.PNG'
    ax.set_legend(units = unit)
    plt.savefig(filename)
    plt.show()        


def get_monthly_data(yearly_df, year, averge_ap_data):
    
    for month in unique_months:
        #Check to make sure data exists for current location ID during current year and current month
        if ((yearly_df['Year'] == year) & (yearly_df['Month'] == month)).any():
            #Create DataFrame for current year
            monthly_df = yearly_df.loc[yearly_df['Month'] == month]
            #Calculate average atmospheric pressure rounded to 2 decimal places
            average_ap = np.around(np.average(monthly_df['AtmosphericPressure'].values),2)
            #Append data to average atmospheric pressure data list
            averge_ap_data.append([year,month,average_ap])
            
    return averge_ap_data
            
def atmospheric_pressure_data(l_id,average_ap_data,df):
 
    #Create DataFrame for atmospheric pressure
    atmospheric_pressure_df = pd.DataFrame(average_ap_data,columns=('Year','Month','Avg_Atmospheric_Pressure'))   
    #Replace blank and NaN entries with 0s  
    #Update category of Month column
    atmospheric_pressure_df['Month'] = atmospheric_pressure_df['Month'].astype(cat_type) 
    #Pivot data to allow Year to be on the x-axis and Month to be on the y-axis with the data occupying the values section of the dataframe being the average atmospheric pressure values
    pivot_df = atmospheric_pressure_df.pivot('Month','Year','Avg_Atmospheric_Pressure')  
    #Replace blank and NaN entries with 0s 
    pivot_df.fillna(0, inplace=True)   

    return pivot_df 

def pivot_tables(average_speed_df):
    
    #Create new DataFrame for wind speed data
    wind_speed_df = average_speed_df[['Year','Location','AverageWindSpeed']]
    #Set variable as Year
    order = wind_speed_df['Year']
    #Pivot data to set DataFrame up for lineplot
    wind_speed_df_wide = wind_speed_df.pivot('Year', 'Location','AverageWindSpeed')
    #Reindex so that year is the index. this allows us to plot all locations on the graph
    wind_speed_df_wide = wind_speed_df_wide.reindex(order, axis=0)
    
    #Create new DataFrame for wind gust data
    wind_gust_df = average_speed_df[['Year','Location','AverageGustSpeed']]
    #Set variable as Year
    order = wind_gust_df['Year']
    #Pivot data to set DataFrame up for lineplot
    wind_gust_df_wide = wind_gust_df.pivot_table(index='Year', columns='Location', values='AverageGustSpeed')
    #Reindex so that year is the index. this allows us to plot all locations on the graph
    wind_gust_df_wide = wind_gust_df_wide.reindex(order, axis=0)
    
    return wind_speed_df_wide,wind_gust_df_wide

def line_plot(dataframes):

    titles = ['Average Wind Speed in Knots (kn) Per Year','Average Gust in Knots (kn) Per Year']
    #Set Seaborn grid type
    for i in range(0,len(dataframes)):    
        sns.set_style('darkgrid')
        filename = 'images\\' + titles[i] + '.PNG'
        #Create lineplot
        sns.lineplot(data = dataframes[i])
        plt.title(titles[i])                 
        plt.savefig(filename)
        plt.show()   

def heat_map(location_name,pivot_df):
    
    #Set Seaborn grid type
    sns.set_style('darkgrid')    
    #Title of graph
    title = 'Average Atmospheric Pressure For - ' + location_name
    filename = 'images\\Graph_' + title + '.PNG'
    plt.title(title)
    #Update the sizing of the Seaborn graph
    sns.set(rc = {'figure.figsize':(15,8)})
    #Set min value to that of the min value of the data
    min_for_location = pivot_df.mask(pivot_df==0).min().min()
    #Plot heatmap with new DataFrame, updated minimum and other settings
    sns.heatmap(pivot_df, vmin= min_for_location,vmax=1025, fmt='.2f',annot=True, cmap='Reds',annot_kws={"fontsize":8})        
    plt.savefig(filename)
    plt.show()   
         
    
def get_yearly_data(location_df, l_id, average_speed_data):
    
    #Initialising average atmospheric pressure array
    average_ap_data = []
    for year in unique_years:
        #Check to make sure data exists for current location ID during current year
        if ((location_df['locationID'] == l_id) & (location_df['Year'] == year)).any():
            #Create DataFrame for current year
            yearly_df = location_df.loc[location_df['Year'] == year]
            
            ws, wd, wg, average_speed_data = get_wind_data(yearly_df, year, average_speed_data, l_id)
            
            if print_windrose:
                wind_rose(wd, ws, l_id, year)
                
            average_ap_data = get_monthly_data(yearly_df, year, average_ap_data)
            
    return average_ap_data
            
                
def data_function(df,map_df): 
    
    #Adding columns for year and month to the DataFrame
    df['Year'] = pd.DatetimeIndex(df['time']).year
    df['Month'] = df['time'].dt.month_name()

    average_speed_data = []
    #First loop cycles through each location ID
    for l_id in unique_locations:
        #Check to make sure data exists for current location ID
        if (df['locationID'] == l_id) .any():
            #Create DataFrame for current location
            location_df = df.loc[(df['locationID'] == l_id)]
            average_ap_data = get_yearly_data(location_df, l_id, average_speed_data)
            
            #Create location name variable for graph title
            location_name = map_df.loc[map_df['locationID'] == l_id]['locationName'].astype("string").item()
            pivot_df= atmospheric_pressure_data(l_id, average_ap_data,df)
            
            if print_graphs:
                heat_map(location_name,pivot_df)
    
    #Create DataFrame with average speed data
    average_speed_df = pd.DataFrame(average_speed_data,columns=('Year','Location','AverageWindSpeed','AverageGustSpeed'))    
    wind_speed_df_wide, wind_gust_df_wide = pivot_tables(average_speed_df)
    dataframes = [wind_speed_df_wide, wind_gust_df_wide]
    
    if print_graphs:
        line_plot(dataframes)
    
def database_entry(data_df,map_df,mergedLocation_Data):

    #Connect to database, tested locally
    connection_to_db = db.connect(user='apple_interview', password='luna123',
                                  host='localhost',
                                  database='apple_interview')
    
    #Initialise cursor
    cursor = connection_to_db.cursor()
    
    #Execute command to create locationmap table
    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS location_map (
                            locationID nvarchar(50) primary key,
                            locationName nvarchar(50)
                            )
                        ''')
    sql_query = 'REPLACE INTO location_map (locationID, locationName) VALUES (%s,%s)'  

    #Loop through DataFrame while executing query with DataFrame values                               
    for row in map_df.itertuples():
        cursor.execute(sql_query,(row.locationID,row.locationName,))
        
    #Commit changes made   
    connection_to_db.commit() 
        
                        
    #Execute command to create locationdata table                    
    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS location_data (
                            locationID nvarchar(50), 
                            time nvarchar(50),
                            atmospheric_pressure int,
                            wind_direction int,
                            wind_speed decimal(8,4),
                            gust decimal(8,4),
                            primary key (locationID, time)
                            )
                        ''')
                        
    #Create query variable 
    sql_query = ' REPLACE INTO location_data (locationID, time, atmospheric_pressure, wind_direction, wind_speed, gust) VALUES (%s,%s,%s,%s,%s,%s)'
    
    #Loop through DataFrame while executing query with DataFrame values    
    for row in data_df.itertuples():
          cursor.execute(sql_query,(row.locationID,row.time,row.AtmosphericPressure,row.WindDirection,row.WindSpeed,row.Gust,))
    
    #Commit changes made 
    connection_to_db.commit() 
    
    #Execute command to create locationMerged table                      
    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS location_merged (
                            locationID nvarchar(50), 
                            locationName nvarchar(50),
                            time nvarchar(50),
                            atmospheric_pressure int,
                            wind_direction int,
                            wind_speed decimal(8,4),
                            gust decimal(8,4),
                            primary key (locationID, time)                          
                            )
                        ''')   
   
    #Create query variable 
    sql_query = ' REPLACE INTO location_merged (locationID, locationName, time, atmospheric_pressure, wind_direction, wind_speed, gust) VALUES (%s,%s,%s,%s,%s,%s,%s)'
    
    #Loop through DataFrame while executing query with DataFrame values    
    for row in mergedLocation_Data.itertuples():
          cursor.execute(sql_query,(row.locationID,row.locationName,row.time,row.AtmosphericPressure,row.WindDirection,row.WindSpeed,row.Gust,))     
          
    #Commit changes made       
    connection_to_db.commit()   
     
    #Close cursor                            
    cursor.close() 
    
if __name__=="__main__":
    
    ''' 
    To run, related csv files must be in same directory as .py file
    csv file names are:
        locationData.csv
        locationMap.csv

    graphs and plots will be stored in images folder which will need to be created and stored in same location as .py file
    
    '''
    
    #Loads csv data into DataFrame
    locationData_csv = pd.read_csv (r'C:\Users\35387\OneDrive\Desktop\Apple Interview\locationData.csv',dtype='unicode')
    locationMap_csv = pd.read_csv (r'C:\Users\35387\OneDrive\Desktop\Apple Interview\locationMap.csv',dtype='unicode')
    
    data_df = pd.DataFrame(locationData_csv)
    data_df = data_df.iloc[1:,:]
    map_df = pd.DataFrame(locationMap_csv)
    
    #To ensure there are no NaN entries in the data    
    data_df.fillna(method='bfill', inplace=True)
    #The current format of the time field will cause issue in MySQL so this is updated
    data_df['time'] = pd.to_datetime(data_df["time"], format="%Y-%m-%dT%H:%M:%SZ")
    
    #merge both data files to create one DataFrame
    mergedLocation_Data = pd.merge(data_df, map_df, on='locationID', how='outer')
    mergedLocation_Data = mergedLocation_Data.iloc[1:,:]
    mergedLocation_Data = mergedLocation_Data[['locationID', 'locationName','time', 'AtmosphericPressure', 'WindDirection', 'WindSpeed', 'Gust']]
    
    #Send data to database
    database_entry(data_df,map_df,mergedLocation_Data)  
    
    #Category values for months
    month_cat = ['January','February','March','April','May','June','July','August','September','October','November','December']
    #Set category type
    cat_type = CategoricalDtype(categories=month_cat, ordered=True)
    
    #Adding columns for year and month to the DataFrame
    mergedLocation_Data['Year'] = pd.DatetimeIndex(mergedLocation_Data['time']).year
    mergedLocation_Data['Month'] = mergedLocation_Data['time'].dt.month_name()
    
    #Creating global variables 
    global unique_locations, unique_years, unique_months,print_windrose, print_graphs, display_to_console
    
    unique_locations = mergedLocation_Data['locationID'].unique()
    unique_years = mergedLocation_Data['Year'].unique()
    unique_months = mergedLocation_Data['Month'].unique()
    
    print_windrose= True
    print_graphs = True

    
    #Initialising average speed list
    average_speed_data = []
    
    #Updating data fields to numeric datatype
    mergedLocation_Data[['WindSpeed','Gust', 'AtmosphericPressure','WindDirection']] = mergedLocation_Data[["WindSpeed", "Gust", 'AtmosphericPressure','WindDirection']].apply(pd.to_numeric)
    
    #Call data function
    data_function(mergedLocation_Data,map_df)
