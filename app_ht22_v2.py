import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import serial
import streamlit as st
st.set_page_config(layout="wide", page_title="Monitoramento de Energia Solar") #, page_icon="sol"
# dashboard title

st.title("Real-Time / Monitoramento Solar")

#Conexão com o Arduino

arduino = serial.Serial(port='COM8', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS)  # Change the COM port to whichever port your arduino is in

# creating a single-element container.
placeholder = st.empty()

i = 0
previous_temp = 0
previous_umid = 0
temp_record = pd.DataFrame(data=[], columns=['Time', 'Temperature (°C)', 'umidade'])

while True:
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


    df = temp_record
    # create two columns for charts
    with placeholder.container():

        # create three columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Umidade Gauge")
            fig1 = go.Figure(go.Indicator(
                domain={'x': [0, 1], 'y': [0, 1]},
                value=umid,
                mode="gauge+number+delta",
                title={'text': "Umid (%)"},
                delta={'reference': previous_umid},
                gauge={'axis': {'range': [0, 40]}}))
            st.write(fig1)
        with col2:
            st.markdown("### Temperatura Gauge")
            fig2 = go.Figure(go.Indicator(
                domain={'x': [0, 1], 'y': [0, 1]},
                value=temp,
                mode="gauge+number+delta",
                title={'text': "Temperature (°C)"},
                delta={'reference': previous_temp},
                gauge={'axis': {'range': [0, 40]}}))
            st.write(fig2)
        # create three columns
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("### Temperatura Ambiente vs Tempo")
            fig3 = px.line(df, x="Time", y="Temperature (°C)", title='Temperature vs. time')
            st.write(fig3)
        with col4:
            st.markdown("### Umidade vs Tempo")
            fig4 = px.line(df, x="Time", y="umidade", title='Umidade vs. time')
            st.write(fig4)

    time.sleep(1)
    i += 1
    previous_temp = temp
    previous_umid = umid
temp_record.to_csv('temperature_record.csv', index=False)

if arduino.isOpen() == True:
    arduino.close()


