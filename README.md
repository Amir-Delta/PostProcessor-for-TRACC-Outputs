# Introduction
The python scripts in this rewpository allow you to postprocess Basemap TRACC's outputs and create a fine-level accessibility score similar to what is developed in [this study](Developing%20a%20Census%20Block%20Level%20Accessibility%20Measure%20for%20St.%20Louis%20Metropolitan%20Area.pdf). 

## Before you start 
* [The study](Developing%20a%20Census%20Block%20Level%20Accessibility%20Measure%20for%20St.%20Louis%20Metropolitan%20Area.pdf) which is the basis of the development of these python scripts, makes several assumptions including the shape of the accessibility function. Understanding these assumptions help you modify the python scripts to fit your data, geography, and accessibility function assumption. 

### Software versions
The script is tested to work with python version 3.7, and outputs of TRACC version 


# Data sources:
Although in [this study](Developing%20a%20Census%20Block%20Level%20Accessibility%20Measure%20for%20St.%20Louis%20Metropolitan%20Area.pdf), the data on points of interest was obtained internally, OpenStreetMap provides datasets on points of interest for many regions worldwide.\
To obtain OpenStreetMap data, visit [Geofabrik's free download server](https://download.geofabrik.de/) and navigate to the page that represent your geographic region of interest.\
For Missouri, US for example, the latest OpenStreetMap data in shapefile format can be obtained in [this page](https://download.geofabrik.de/north-america/us/missouri.html) and from [this link](https://download.geofabrik.de/north-america/us/missouri-latest-free.shp.zip). After downloading and unzipping the shapefile data folder for Missouri, US, you would be able to open it in a GIS software and access points of interest in a layer named gis_osm_pois_free_1.shp


