import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os



DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)



st.header('Pharmacy Sheet')

if 'active_page' not in st.session_state:
   st.session_state.active_page=None


def craw1():

    with st.form(key='from_doct',clear_on_submit=True):
     PName=st.selectbox('Select Patient Name:',['Name'])
     Reg_no=st.text_input('Reg_no:')
     Age=st.number_input('Age:',min_value=0,max_value=100)
     Sex=st.selectbox('Sex:',['male','female'])
     Mdetails=st.text_area('Medication Details:')
     Dname=st.text_input('Doctor Name:')
     Amount=st.text_area('Amount for Medication:')
     Submit=st.form_submit_button('Confirm 💊')

     if Submit:
        st.success(f'Medication for {PName} Confirmed!')
     
def craw2():
    st.info('PATIENT MEDICATION HISTORY')
    

    st.session_state.datas=pd.DataFrame({
       'Reg_No':pd.Series(dtype='str'),
       'Name':pd.Series(dtype='str'),
       'Age':pd.Series(dtype='int'),
       'Sex':pd.Series(dtype=str),
       'Doctor':pd.Series(dtype='str'),
       'Medication Details':pd.Series(dtype='str'),
       'Amount':pd.Series(dtype='str')
    })

    st.dataframe(st.session_state.datas,
      key='pharmacy_data_editor')    


st.sidebar.header('Pharmacy Panel💊')

if st.sidebar.button('View💻'):
   st.session_state.active_page='from_doctor'

if st.sidebar.button('History📜'):
   st.session_state.active_page='History'


if st.session_state.active_page=='from_doctor':
   craw1()

if st.session_state.active_page=='History':
   craw2()

else:

   st.info('👈Select an Option from the Sidebar')
