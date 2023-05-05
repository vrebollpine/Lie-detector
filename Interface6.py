import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque

import serial     # library used to communicate with serial port
import re         # library used to extract data from string
import time       # library used to create periodic reading event
 
X_humd=deque(maxlen=20)
#X_humd.append(1)
X_heard=deque(maxlen=20)
#X_temp.append(1)
heard_list = deque(maxlen=20)
#temp_list.append(1)
humd_list = deque(maxlen=20)
#humd_list.append(1)
co2_values = deque(maxlen=100) # Define deque object to store CO2 values

#arduinoData = []       # list to save data from Arduino
ser = serial.Serial()  # create a serial instance
ser.port = 'COM1'      # set the port number
ser.baudrate = 9600    # set the baudrate of the port


ser.open()

serial_read_state = True
def serialRead(ser, cmd):   #Serial read function
    global serial_read_state
    if (serial_read_state==True):   # Avoid reading serial port at the same time -> conflict
        serial_read_state=False
        read_command = (cmd+'\n')
        ser.write(read_command.encode("utf-8"))
        message = ser.readline() # read a line of data from serial port
        print(message)
        data_string = message.decode("utf-8") # decode the received message to string
        print(data_string)
        data = re.findall('[\d]+[.,\d]+', data_string) # extract values from string in a list
        data = float(data[0])
        serial_read_state=True
    else:
        time.sleep(0.1)
        data=serialRead(ser, cmd)
    return data 

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.Div([
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1000    # update every second
        ),
    ]),
    html.Div([
        dcc.Graph(id='live-graph2', animate=True),
        dcc.Interval(
            id='graph-update2',
            interval=1000    # update every second
        ),
    ])
    ,dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1000 # Update graph every second
        )
    
  ]
)

@app.callback(Output('live-graph', 'figure'),    # callback to update live-graph
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(input_data):  #function to update data of live-graph
    if len(X_humd)==0:
        X_humd.append(1)
    else:
        X_humd.append(X_humd[-1]+1)
    humd = serialRead(ser, 'Humd')
    humd_list.append(humd)   # display the first Arduino data from the list
    data = go.Scatter(
            x=list(X_humd),
            y=list(humd_list),
            name='Scatter',
            mode= 'lines+markers'
            )
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X_humd),max(X_humd)]),   # x-> time step range
                                                yaxis=dict(range=[0,100]),
                                                xaxis_title='Time Step (2s)',
                                                yaxis_title='Humudity (%)')} # y-> temp range

@app.callback(Output('live-graph2', 'figure'),  #callback to update live-graph2
              [Input('graph-update2', 'n_intervals')])
def update_graph_scatter_heard(input_data): #function to update data of live-graph2
    #X_heard.append(X_temp[-1]+1)
    
    if len(X_heard)==0:
        X_heard.append(1)
    else:
        X_heard.append(X_heard[-1]+1)
    
    heard = serialRead(ser,'Heart')
    heard_list.append(heard)
    data = go.Scatter(
            x=list(X_heard),
            y=list(heard_list),
            name='Scatter',
            mode= 'lines+markers'
            )
    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X_heard),max(X_heard)]),   # x-> time step range
                                                yaxis=dict(range=[0,100]), 
                                                xaxis_title='Time Step (2s)',
                                                yaxis_title='Heard Rate',)} # y-> heard rate range

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph(n):
    # Read CO2 value from serial port
    co2_value = float(ser.readline().decode().strip())
    co2_values.append(co2_value)
    trace = go.Scatter(
        x=list(range(len(co2_values))),
        y=list(co2_values),
        mode='lines+markers'
    )
    layout = go.Layout(
        xaxis=dict(range=[0, 100]),
        yaxis=dict(range=[0, max(co2_values) + 50])
    )
    return {'data': [trace], 'layout': layout}



if __name__ == '__main__':
    app.run_server(port=8044, debug=False) 