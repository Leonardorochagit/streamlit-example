import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import serial
import streamlit as st
st.set_page_config(layout="wide", page_title="Monitoramento de Energia Solar") #, page_icon="sol"

arduino = serial.Serial(port='COM8', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS)  # Change the COM port to whichever port your arduino is in

# Use the full page instead of a narrow central column


#https://medium.com/codefile/customizing-streamlit-columns-4bfd58fcb7c9
col1, col2, col3 = st.columns([3,3, 2]) #Crio as colunas col1, preenchimento, col2, col3

with col1:
    gauge_placeholder = st.empty()
with col2:
    chart_placeholder = st.empty()

with col3:
    chart2_placeholder = st.empty()

def temp_gauge(temp, previous_temp, gauge_placeholder):
    fig = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=temp,
        mode="gauge+number+delta",
        title={'text': "Temperature (°C)"},
        delta={'reference': previous_temp},
        gauge={'axis': {'range': [0, 40]}}))

    gauge_placeholder.write(fig)


def temp_chart(df, chart_placeholder):
    fig = px.line(df, x="Time", y="Temperature (°C)", title='Temperature vs. time')
    chart_placeholder.write(fig)

#Gráfico de Umidade

def umid_chart(df, chart2_placeholder):

    fig = px.line(df, x="Time", y="umidade", title='Umidade vs. time')
    chart2_placeholder.write(fig)

if arduino.isOpen() == False:
    arduino.open()

'''
####Montando as visualizações dos gráficos lado a lado
col1_1, col1_2 = st.columns(2)
with col1_1:
    st.plotly_chart(temp_chart, use_container_width=True)
with col1_2:
    st.plotly_chart(umid_chart, use_container_width=True)
'''

i = 0
previous_temp = 0
temp_record = pd.DataFrame(data=[], columns=['Time', 'Temperature (°C)', 'umidade'])

while True:  #i < 500 # Change number of iterations to as many as you need
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    try:
        #temp = round(float(arduino.readline().decode().strip('\r\n')), 1)
        line = arduino.readline()
        lista = line.decode("utf-8")
        medicao = (lista.split(':', 5))
        temp = float(((medicao[2][0:6])))
        umid = float((medicao[1][0:6]))
    except:
        pass

    temp_record.loc[i, 'Time'] = current_time
    temp_record.loc[i, 'Temperature (°C)'] = temp
    temp_record.loc[i, 'umidade'] = umid

    temp_gauge(temp, previous_temp, gauge_placeholder)
    temp_chart(temp_record, chart_placeholder)
    umid_chart(temp_record, chart2_placeholder)
    time.sleep(1)
    i += 1
    previous_temp = temp

temp_record.to_csv('temperature_record.csv', index=False)

if arduino.isOpen() == True:
    arduino.close()


