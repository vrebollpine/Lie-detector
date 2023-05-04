import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from collections import deque
import serial
import re

# Connect to Arduino board via serial port
ser = serial.Serial('COM1', 9600)

# Initialize deque data structures to store data for each sensor
hr_data = deque(maxlen=50)
co2_data = deque(maxlen=50)
humd_data = deque(maxlen=50)

# Define callback functions to update data for each sensor
def update_hr_data():
    # Send command to Arduino board to obtain heart rate data
    ser.write(b'Heart\n')
    # Read response from serial port and extract numerical value using regex
    response = ser.readline().decode().strip()
    hr_value = int(re.findall(r'\d+', response)[0])
    # Add heart rate data to deque
    hr_data.append(hr_value)

def update_co2_data():
    # Send command to Arduino board to obtain CO2 data
    ser.write(b'CO2\n')
    # Read response from serial port and extract numerical value using regex
    response = ser.readline().decode().strip()
    co2_value = int(re.findall(r'\d+', response)[0])
    # Add CO2 data to deque
    co2_data.append(co2_value)

def update_humd_data():
    # Send command to Arduino board to obtain humidity data
    ser.write(b'Humd\n')
    # Read response from serial port and extract numerical value using regex
    response = ser.readline().decode().strip()
    humd_value = int(re.findall(r'\d+', response)[0])
    # Add humidity data to deque
    humd_data.append(humd_value)

# Create Dash app
app = dash.Dash(__name__)

# Define layout for app
app.layout = html.Div(children=[
    html.H1(children='Sensor Data Dashboard'),
    dcc.Graph(id='hr-graph'),
    dcc.Graph(id='co2-graph'),
    dcc.Graph(id='humd-graph'),
    dcc.Interval(
        id='interval-component',
        interval=2000, # Update every 2 seconds
        n_intervals=0
    )
])

# Define callback functions to update graphs
@app.callback(Output('hr-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_hr_graph(n):
    update_hr_data()
    # Create scatter plot with heart rate data
    data = {'x': list(range(len(hr_data))), 'y': list(hr_data), 'type': 'scatter', 'name': 'Heart Rate'}
    layout = {'title': 'Heart Rate', 'xaxis': {'title': 'Time'}, 'yaxis': {'title': 'Heart Rate (BPM)'}}
    return {'data': [data], 'layout': layout}

@app.callback(Output('co2-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_co2_graph(n):
    update_co2_data()
    # Create scatter plot with CO2 data
    data = {'x': list(range(len(co2_data))), 'y': list(co2_data), 'type': 'scatter', 'name': 'CO2'}
    layout = {'title': 'CO2', 'xaxis': {'title': 'Time'}, 'yaxis': {'title': 'CO2 Concentration (ppm)'}}
    return {'data': [data], 'layout': layout}

@app.callback(Output('humd-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_humd_graph(n):
    update_humd_data()
    data = {'x': list(range(len(humd_data))), 'y': list(humd_data), 'type': 'scatter', 'name': 'humd'}
    layout = {'title': 'humd', 'xaxis': {'title': 'Time'}, 'yaxis': {'title': 'humd %'}}
    return {'data': [data], 'layout': layout}


if __name__ == '__main__':
    app.run_server(port=8044, debug=False) 
