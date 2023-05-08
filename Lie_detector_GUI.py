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
X_CO2=deque(maxlen=20)
X_heart=deque(maxlen=20)
heart_list = deque(maxlen=20)
humd_list = deque(maxlen=20)
CO2_list = deque(maxlen=20)

ser = serial.Serial()  
ser.port = '/dev/cu.usbmodem14101'     
ser.baudrate = 115200   

def float_message(data):
    
     return [float(s) for s in data]

ser.open()

serial_read_state = True

def serialRead(ser, cmd):   
    global serial_read_state
    global data
    if (serial_read_state==True):   
        serial_read_state=False
        read_command = (cmd+'\n')
        ser.write(read_command.encode("utf-8"))
        message = ser.readline() # read a line of data from serial port
        data_string = message.decode("utf-8")
        data = re.findall('[\d]+[.,\d]+', data_string) # extract values from string in a list
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
            interval=5*1000   
        ),
    ]),
    html.Div([
        dcc.Graph(id='live-graph2', animate=True),
        dcc.Interval(
            id='graph-update2',
            interval=5*1000  
        ),
    ]),
    html.Div([
        dcc.Graph(id='live-graph3', animate=True),
        dcc.Interval(
            id='graph-update3',
            interval=5*1000    
        ),
    ])
    
  ]
)


@app.callback(Output('live-graph', 'figure'),  
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter_heart(input_data): 
    
    if len(X_heart)==0:
        X_heart.append(1)
    else:
        X_heart.append(X_heart[-1]+1)
    
    heart = float(serialRead(ser,'heartRate')[0])
    heart_list.append(heart+1)
    data_heart = go.Scatter(
            x=list(X_heart),
            y=list(heart_list),
            name='Scatter',
            mode= 'lines+markers'
            )
    return {'data': [data_heart],'layout' : go.Layout(xaxis=dict(range=[min(X_heart),max(X_heart)]),  
                                                yaxis=dict(range=[0,200]), 
                                                xaxis_title='Time Step ',
                                                yaxis_title='Heart rate')} 


@app.callback(Output('live-graph2', 'figure'), 
              [Input('graph-update2', 'n_intervals')])
def update_graph_scatter_CO2(input_value):
    global X_CO2, CO2_list
    
    if len(X_CO2) == 0:
        X_CO2.append(1)
    else:
        X_CO2.append(X_CO2[-1]+1)

    CO2 = float(serialRead(ser,'concentration')[1])
    CO2_list.append(CO2)

    data_CO2 = plotly.graph_objs.Scatter(
        x=list(X_CO2),
        y=list(CO2_list),
        name='Scatter',
        mode='lines+markers'
    )

    return {'data': [data_CO2], 'layout' : go.Layout(xaxis=dict(range=[min(X_CO2),max(X_CO2)]),
                                                     yaxis=dict(range=[min(CO2_list),max(CO2_list)+50]),
                                                     xaxis_title='Time Step',
                                                    yaxis_title='CO2 concentration',)}
@app.callback(Output('live-graph3', 'figure'),   
              [Input('graph-update3', 'n_intervals')])
def update_graph_scatter(input_data):  
    if len(X_humd)==0:
        X_humd.append(1)
    else:
        X_humd.append(X_humd[-1]+1)

    humd = float(serialRead(ser, 'humd')[2])
    humd_list.append(humd)   
    data_humd = go.Scatter(
            x=list(X_humd),
            y=list(humd_list),
            name='Scatter',
            mode= 'lines+markers'
            )
    return {'data': [data_humd],'layout' : go.Layout(xaxis=dict(range=[min(X_humd),max(X_humd)]),  
                                                yaxis=dict(range=[20,max(humd_list)+10]),
                                                xaxis_title='Time Step',
                                                yaxis_title='Humidity (%)')} 


if __name__ == '__main__':
    app.run_server(port=8044, debug=False) 