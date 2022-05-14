# Introduction
The python scripts in this repository allow you to postprocess Basemap TRACC's outputs and create a US Census Block-level accessibility score similar to what is developed in [this study](Developing%20a%20Census%20Block%20Level%20Accessibility%20Measure%20for%20St.%20Louis%20Metropolitan%20Area.pdf). 

# Before you start 
* [The study](Developing%20a%20Census%20Block%20Level%20Accessibility%20Measure%20for%20St.%20Louis%20Metropolitan%20Area.pdf) which is the basis of the development of python scripts within this repository, makes several assumptions including the shape of the accessibility function. Understanding these assumptions help you modify the python scripts to fit your data, geography, and accessibility function assumption. 
* [The study](Developing%20a%20Census%20Block%20Level%20Accessibility%20Measure%20for%20St.%20Louis%20Metropolitan%20Area.pdf) uses TRACC to calculate travel times and distances between origins and destinations as part of calculating accessibility score. 

## Software versions
The scripts within this repository are tested to work with python version 3, and outputs of TRACC version 2.0.2.

## Running TRACC
* We assume that you are familiar with how to run Basemap TRACC. If not, visit https://www.basemap.co.uk/tracc/ to learn more about the software. 
* To run TRACC version 2.0.2, we define a project within the software and calculate the travel times and distances using Origin Destination tool in Calculation tab. Origin Destination tool calculates travel times and distances between origins and destinations for a specific mode of interest. 
* In [the study](Developing%20a%20Census%20Block%20Level%20Accessibility%20Measure%20for%20St.%20Louis%20Metropolitan%20Area.pdf) origins are considered to be the centroid of US Census Blocks within the St. Louis Metropolitan Area, Missouri, USA. However, you can choose the centroid of any geography as your origins.
* In [the study](Developing%20a%20Census%20Block%20Level%20Accessibility%20Measure%20for%20St.%20Louis%20Metropolitan%20Area.pdf) destinations  are considered to be the location of points of interest within the St. Louis Metropolitan Area, Missouri, USA.
* When importing origins and destinations, consider the following,
	* When using Data Import Wizard to import origins (here, the centroid of US Census Blocks), select the column that is the origin's unique identifier in the 'Name' drop down list. This identifier would be used in the scripts to match TRACC outputs and create an accessibility score for each origin. 
	* When using Data Import Wizard to import destinations (here, the location of points of interest), select the column that is the destination's unique identifier in the 'Name' drop down list and the column that is the category of the points of interest in the 'Descripotion' drop down list.
* TRACC version 2.0.2, saves the travel time and distance estimates in a table named Result, in a Microsoft SQL Server database.
* The python scripts in this repository obtain estimates from the Result table and perform some post-processing tasks to calculate the accessibility score for each origin. 

## Data on points of interest
Although in [this study](Developing%20a%20Census%20Block%20Level%20Accessibility%20Measure%20for%20St.%20Louis%20Metropolitan%20Area.pdf), the data on points of interest was obtained internally, OpenStreetMap provides datasets on points of interest for many regions worldwide.\
To obtain OpenStreetMap data, visit [Geofabrik's free download server](https://download.geofabrik.de/) and navigate to the page that represent your geographic region of interest. For Missouri, US, for example, the latest OpenStreetMap data in shapefile format can be obtained in [this page](https://download.geofabrik.de/north-america/us/missouri.html) and from [this link](https://download.geofabrik.de/north-america/us/missouri-latest-free.shp.zip). After downloading and unzipping the shapefile data folder for Missouri, US, you would be able to open it in a GIS software and access points of interest in a layer named gis_osm_pois_free_1.shp

# The scripts
There are two scripts within this repository. Although they are pretty similar in structure, they use different functions to calculate accessibility score.
* [AccessibilityScore_TravelTime](AccessibilityScore_TravelTime.py) calculates accessibility score based on travel time between origins and destinations. This script is used when travel time is more important to transportation network user than travel distance, for example when travel mode is transit. 
* [AccessibilityScore_TravelDistance](AccessibilityScore_TravelDistance.py) calculates accessibility score based on travel distance between origins and destinations. This script is used when travel distance is more important to transportation network user than travel time, for example when travel mode is walk.  

## Variables and parameters
In the beginning of each script, a few variables and scripts need to be specified. These variables are as follows:
* **Server**: The name of Microsoft SQL Server on which TRACC run output is stored,
* **Database**: The name of Microsoft SQL database on which TRACC run output is stored. Note that every time a new project is defined in TRACC, a new database is created in Microsoft SQL Server to store the outputs of runs associated with that project,
* **ResultHeaderId**: An integer that identifies the specific TRACC run for which the accessibility score is calculated. The first run in a new TRACC project is assigned a **ResultHeaderId** of **1**. The **ResultHeaderId** increases one by one in the subsequent runs,
* **output**: The path and name of the CSV file that will be created by the script and contain the accessibility score for each origin,
* Saturation and weight for each point of interest category, travel distance (**threshold_miles** in AccessibilityScore_TravelTime) or travel time (**threshold_minutes** in AccessibilityScore_TravelDistance) catchments, and **beta**: These are parameters that define the shape of accessibility function. See [the study](Developing%20a%20Census%20Block%20Level%20Accessibility%20Measure%20for%20St.%20Louis%20Metropolitan%20Area.pdf) for more information on these parameters. 

## The outputs
The output of each of these scripts is a CSV file with two columns. The first column, **OrigName**, is an ID that identifies the origin (here, US Census Block) for which the accessibility score is calculated; the second column, **score**, is the accessibility score for that origin.