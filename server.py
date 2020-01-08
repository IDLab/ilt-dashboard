"""
This script is the running process of the server providing the dashboard.
"""

import argparse
import csv
import io
import json
import os

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import flask
import pandas as pd

# own imports
from connect_database import cnx

mapbox_access_token = os.environ['TOKEN']

# Read arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('specification_file', help="Specification file to read in.")
args = parser.parse_args()
table_name = args.specification_file.split('/')[-1].split('.')[0]

# Selects all data from KvK_Locaties and add a column `Description' with the corresponding SBI-description
# currently limited at 10000 to not overload the browser
try:
	df = pd.read_sql("(SELECT * FROM " + table_name + " LEFT JOIN sbi ON " + table_name + ".SBI = sbi.SBI) ORDER BY RAND() LIMIT 10000;", con=connect_database.cnx)
except IOError:
	raise Exception("Database does not exists or is empty.")

# Make a list of cities for the dropdown menu
try:
	steden = pd.read_sql("SELECT distinct City FROM " + table_name + " ORDER BY City;", con=cnx)
except IOError:
	raise("Database does not exists or is empty")

steden = steden["City"]

# Make a list of SBI numbers for the dropdown menu
SBIs = pd.read_sql("SELECT distinct SBI FROM " + table_name + " ORDER BY SBI;", con=cnx)
SBIs = SBIs["SBI"]

app = dash.Dash()

# read configfile for tooltip
try:
	with open(args.specification_file) as confFile:
			specTooltip=confFile.read()
except:
	raise Exception("Failed to load configuration file")

specTooltip = json.loads(specTooltip)

try:
	specTooltip = specTooltip["tooltip"]
except:
	raise("Failed to load tooltip configuration")

print(specTooltip)


def tooltip(df):
    text  = ""
    for field in specTooltip:
        text = text + field + ": " + df[field] + "<br />"
    return text

app.layout = html.Div([
    
    # Div containing the map and datapoints
    html.Div([
        html.Div([
            dcc.Graph(
                id = "mapbox",
                figure={
                    "data": [
                        dict(
                            type = "scattermapbox",
                            lat = df['Latitude'],
                            lon = df['Longitude'],
                            mode = "markers",
                            marker = dict(size = 10),
                            text = tooltip(df))
                    ],
                    'layout': dict(
                        autosize = True,
                        hovermode = "closest",
                        clickmode = 'event+select',
                        margin = dict(l = 0, r = 0, t = 0, b = 0),
                        mapbox = dict(
                            accesstoken = mapbox_access_token,
                            bearing = 0,
                            center = dict(lat = 52, lon = 5),
                            pitch = 0,
                            zoom = 8
                        )
                    )
                },
                style = {"height": "100%"}
            )
        ],
            style = {"height": "100%", "width": "100%"}
        )
        
    ], 
    # Define style for the mapbox
    style = {"border-style": "solid", "height": "95vh", "width": "80%"}),
    
    # Div containing the side bar with menu options
    html.Div([
        html.Div([
            # Dropdown menu for city selection
            html.P(
                "Selecteer een stad:"
            ),
            html.Div([
                dcc.Dropdown(
                    id = "dist-drop",
                    options = [{"label": i, "value": i} for i in sorted(steden)],
                    placeholder = "Selecteer Stad")
            ],
                style = {"width": "200px"}
            ),
            # Dropdown menu for SBI numbers
            html.P(
                "Selecteer een SBI nummer:"
            ),
            html.Div([
                dcc.Dropdown(
                    id = "sbi",
                    options = [{"label": i, "value": i} for i in sorted(SBIs)],
                    placeholder = "Selecteer SBI")
            ],
                style = {"width": "200px"}
            ),
            html.Div([
                html.A("Download",id="dlLink", href="dash/urlToDownload?City=Leeuwarden")
            ],
                style = {"marginTop": "10px"}
            )
        ], style = {"paddingLeft": "15px",
                    "paddingBottom": "20px"}
        )    
    ], 
    # Define style for the menu list
    style = {"position": "absolute", 
                "top": "8px", "right": "10px", "width": "19%"}
                
    ),
    
    # Div containing the info box
    html.Div([
    html.H1('Information on selected point'),
    html.Div(id='tabs-content-example')
])
    
    
    
])

@app.server.route('/dash/urlToDownload', methods=['GET'])
def download_csv():
    city = flask.request.args.get("City")
    SBI = flask.request.args.get("SBI")
    if(SBI == ""): SBI = None
    if(city == ""): city = None
    params = {
        "cn": city,
        "sbi": SBI
    }
    query = CreateQuery(city, SBI)

    df = pd.read_sql(query, con=cnx, params=params)
    return df.to_string(), 200, {'Content-type': 'text/csv'}


def CreateQuery(city_value, sbi):
    query = "SELECT * FROM " + table_name + " "

    if city_value != None or sbi != None:
        query += "WHERE "

    constraints = [
        "City=%(cn)s " if city_value != None else None,
        "SBI=%(sbi)s " if sbi != None else None
    ]

    query += " and ".join(filter(lambda x:x != None, constraints))
    return query


@app.callback(
    [Output(component_id='dlLink',component_property='href'),
    Output(component_id='mapbox',component_property='figure')],

    [Input(component_id='dist-drop', component_property='value'), 
    Input(component_id='sbi', component_property='value')]
)

#Function used for updating map
def update_map(city_value, sbi):
    global df
    # Generate query
    query = "SELECT kvk.*, sbi.Description FROM kvk LEFT JOIN sbi ON kvk.SBI = sbi.SBI "
    # What to filter
    params = {
        "cn": city_value,
        "sbi": sbi
    }

    #  Do we need a where clause?
    if city_value != None or sbi != None:
        query += "WHERE "

    #  If we have a where clause, which constraints do we need to add?
    constraints = [
        "City=%(cn)s " if city_value != None else None,
        "kvk.SBI=%(sbi)s " if sbi != None else None
    ]

    # Add constraints to query
    query += " and ".join(filter(lambda x:x != None, constraints))

    # Give a random ordering
    query += "ORDER BY RAND() LIMIT 10000;"

    df = pd.read_sql(query, con=cnx, params=params)
    if len(df) == 0:
        df = dfAll

    luc = [df['Latitude'].min(), df['Longitude'].min()]
    rdc = [df['Latitude'].max(), df['Longitude'].max()]
    
    # Return download link and update the map
    return ["dash/urlToDownload?City="+ (city_value or "") + "&SBI=" + str(sbi
or ""), {
        "data": [
            dict(
                type = "scattermapbox",
                lat = df["Latitude"],
                lon = df["Longitude"],
                mode = "markers",
                marker = dict(size = 14),
                text = tooltip(df)
                )],
        'layout': dict(
            autosize = True,
            hovermode = "closest",
            margin = dict(l = 0, r = 0, t = 0, b = 0),
            mapbox = dict(
                accesstoken = mapbox_access_token,
                bearing = 0,
                center = dict(lat = (luc[0]+rdc[0])/2, lon = (luc[1]+rdc[1])/2), # Automatically center map
                pitch = 0,
                zoom = 9
            )
        )
    }]
    
# Function called when points in the map are selected    
@app.callback(Output('tabs-content-example', 'children'),
              [Input('mapbox', 'clickData'), Input('mapbox', 'selectedData')])
def render_content_clicked(clickData, selectedData):
    global df

    # If nothing is selected (called when program is started).
    if clickData == None and selectedData == None:
        # Update the table
        return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        )
    
    # If a point is selected (mouse click)
    if dash.callback_context.triggered[0]["prop_id"] == "mapbox.clickData":
        
        # Select the point in the dataframe where longitude and latitude match
        dff = df.loc[df['Latitude'] == clickData['points'][0]['lat']] 
        dff = dff.loc[dff['Longitude'] == clickData['points'][0]['lon']]
        
        return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=dff.to_dict('records'),
        )
    # If multiple points are selected (lasso tool)
    elif dash.callback_context.triggered[0]["prop_id"] == "mapbox.selectedData":
        # Collect all selected points from the dataframe
        selected = pd.DataFrame()
        for i in range(len(selectedData['points'])):
            selected = selected.append(df.iloc[[selectedData['points'][i]['pointIndex']]])
        
        return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=selected.to_dict('records'),
        )
    # Empty return for other input
    else:
        return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        )


if __name__ == '__main__':
    app.run_server(debug=True)
