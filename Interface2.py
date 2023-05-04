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
X_CO2=deque(maxlen=20)
#X_CO2.append(1)
X_heard=deque(maxlen=20)
#X_temp.append(1)
heard_list = deque(maxlen=20)
#temp_list.append(1)
humd_list = deque(maxlen=20)
#humd_list.append(1)
CO2_list = deque(maxlen=20)
#CO2_list.append(1)

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
            interval=2*1000    # update every 5 seconds 
        ),
    ]),
    html.Div([
        dcc.Graph(id='live-graph2', animate=True),
        dcc.Interval(
            id='graph-update2',
            interval=2*1000    # update every 5 seconds
        ),
    ])
    ,html.Div([
        dcc.Graph(id='live-graph3', animate=True),
        dcc.Interval(
            id='graph-update3',
            interval=2*1000    # update every 5 seconds
        ),
    ])
    
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


@app.callback(Output('live-graph3', 'figure'),  #callback to update live-graph3
              [Input('graph-update3', 'n_intervals')])
def update_graph_scatter_CO2(input_value):
    global X_CO2, CO2_list
    
    if len(X_CO2) == 0:
        X_CO2.append(0)
    else:
        X_CO2.append(X_CO2[-1]+1)

    CO2_list.append(input_value)

    data_CO2 = plotly.graph_objs.Scatter(
        x=list(X_CO2),
        y=list(CO2_list),
        name='Scatter',
        mode='lines+markers'
    )

    return {'data': [data_CO2], 'layout' : go.Layout(xaxis=dict(range=[min(X_CO2),max(X_CO2)]),yaxis=dict(range=[min(CO2_list),max(CO2_list)]),)}


if __name__ == '__main__':
    app.run_server(port=8044, debug=False) 