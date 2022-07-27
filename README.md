# Apple_Interview
Using the technology of your choice: - Save the provided data-set into a database - Show / visualise the data 

For this project I decided to use the Python programming language as I felt this was the best choice because of the capabilities of python in data presentation. Python is widely used in artificial intelligence with multiple libraries that could help with the data provided. One such library that I was keen to use was Pandas which allows users to create dataframes from sources such as the csv files provided. Another such library that would be very useful for this project is Seaborn which is a data visualisation tool that uses matplotlib, another useful library. The next decision that had to be made was the database that would be used. For this I decided on using MySQL as I had previous expierence using this application. 

As the data provided relates to wind and atmospheric pressure data, I researched how best to display the information. I discovered that the information provided could be used to create a wind rose, which also had a python library, this was called WindRoseAxes. Now that I unerstood the task I was able to begin.

First I began by establishing a connection to the database so that I could create tables and add data. To do this I used another python library provided by MySQL called mysql.connector.

```python
connection_to_db = db.connect(user='apple_interview', password='luna123',
                                  host='localhost',
                                  database='apple_interview')

cursor = connection_to_db.cursor()
```
