# Apple_Interview
Using the technology of your choice: - Save the provided data-set into a database - Show / visualise the data 

For this project I decided to use the Python programming language as I felt this was the best choice because of the capabilities of python in data presentation. Python is widely used in artificial intelligence with multiple libraries that could help with the data provided. One such library that I was keen to use was Pandas which allows users to create dataframes from sources such as the csv files provided. Another such library that would be very useful for this project is Seaborn which is a data visualisation tool that uses matplotlib, another useful library. The next decision that had to be made was the database that would be used. For this I decided on using MySQL as I had previous expierence using this application. As the data provided relates to wind and atmospheric pressure data, I researched how best to display the information. I discovered that the information provided could be used to create a wind rose, which also had a python library, this was called WindRoseAxes.

Firstly I established connection to the database

```python
    connection_to_db = db.connect(user='apple_interview', password='luna123',
                                  host='localhost',
                                  database='apple_interview')

    cursor = connection_to_db.cursor()
```
Next, I updated the data as it contained some invalid data such as NaN values.

```python
    data_df.fillna(method='bfill', inplace=True)
    data_df['time'] = pd.to_datetime(data_df["time"], format="%Y-%m-%dT%H:%M:%SZ")
```

Before finally adding the data-set to the database
```python
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
    
```
This function acts as the initial function for the data, here columns are added for month and year that will make later operations easier. A for loop is used here to cycle through each location. Checks are also made to ensure some data exists for the station in order to avoid unnecessary operations. Calls to other functions are made to get data for other functions and graphs. 
```python
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
    
```
This function extracts the wind speed, wind direction and wind gust values that will be used in calculations such as the wind rose. Average speeds are also calculated that will be used to compare yearly average wind speeds between locations. The calculated values are returned
```python
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
    
```
This function creates the wind rose using ws and wd which were returned in the previous function. The resulting graph is labeled and saved to the images folder
```python
def wind_rose(wd, ws, l_id, year):
    
    #Create and show Wind Rose Graph
    ax = WindroseAxes.from_ax()
    ax.bar(wd, ws, normed=True, opening=0.8, edgecolor='white')
    unit = str(l_id) + '_' + str(year)
    filename = 'images\WindRose_' + unit + '.PNG'
    ax.set_legend(units = unit)
    plt.savefig(filename)
    plt.show()   
    
```
Sample wind rose.
![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)
