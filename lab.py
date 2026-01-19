import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os



DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.wegsxzwhrdhqsvkuqweg:codexhusseinmartinnkya@aws-1-eu-central-1.pooler.supabase.com:5432/postgres",
)


st.header('Lab sheet')


if 'active_page' not in st.session_state:
   st.session_state.active_page=None

if 'datas' not in st.session_state:
  st.session_state.datas=pd.DataFrame({
         'Reg_No':pd.Series(dtype='str'),
         'Name':pd.Series(dtype='str'),
         'Age':pd.Series(dtype='int'),
         'Sex':pd.Series(dtype=str),
         'Doctor':pd.Series(dtype='str')
   })



def get_patient_name():

   sql="""
       SELECT DISTINCT p_name  FROM doclab WHERE testres IS NULL or testres=''  ORDER BY p_name
"""
   try:
       with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
          with conn.cursor() as cur:
              cur.execute(sql)
              rows=[row[0] for row in cur.fetchall()]
              return rows,None
   except Exception as e:
      return None, str(e)

def patient_details(name):

   sql="""
       SELECT testings,medical_d FROM doclab WHERE p_name=%s LIMIT 1
   """
   try:
        with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (name,))
                details = cur.fetchone()
                return details, None # Returns a dictionary or None
   except Exception as e:
        return None, str(e)

def lab_hist():
    sql="""
       SELECT p_name,testings,medical_d,testres FROM doclab WHERE testres IS NOT NULL ORDER BY p_name
"""
    try:
        with psycopg2.connect(DATABASE_URL,sslmode="require") as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                rows=cur.fetchall()
                return rows,None
    except Exception as e:
        return None,str(e)
    

def update_lab_res(lab_res,patient_name,testings):
   sql="""
       UPDATE doclab
       SET testres =%s
       WHERE p_name=%s AND testings=%s
      

   """
   try:
       with psycopg2.connect(DATABASE_URL,sslmode="require") as conn:
           with conn.cursor(cursor_factory=RealDictCursor) as cur:
               cur.execute(sql,(lab_res,patient_name,testings))
               conn.commit()
       return True,None
   except Exception as e:
         return False,str(e)


def stage1():
    st.info('RESULTS FORM TO DOCTOR')

    names_list,err=get_patient_name()

    if err:
       st.error(f"Error fetching patients names: {err}")
       names_list=["Error loading names"]
    if not names_list:
         names_list=["No patients available"]


    Select=st.selectbox('Select Name:',options=names_list)

    details,details_err=patient_details(Select)
    default_testings = details['testings'] if details else "Details not found"
    default_medical_d = details['medical_d'] if details else "Details not found"
      
    with st.form(key='from_doc',clear_on_submit=True):
        
        TesT=st.text_area('Testings:',value=default_testings,width=400,height=150)
        Dname=st.selectbox('Doctor',['Doctor1','Doctor2','Doctor3'])
        MedI=st.text_area('Medical Details:',value=default_medical_d)
        ResuT=st.text_area('Results:')
    
        Submit=st.form_submit_button('Send Feedback')
     
        if Submit:
           if not ResuT:
            st.error('Fill All the Field')
           else:
              success, err = update_lab_res(ResuT, Select, default_testings)

              if success:
                st.success(f'✅ Results sent successfully for {Select}')
              else:
               st.error(f'❌ Failed to update: {err}')

      

def stage2():

    st.info('REQUEST HISTORY FROM DOCTORS')

    st.session_state.datas=pd.DataFrame({
       
       'Patient Name':pd.Series(dtype='str'),
       'Testings':pd.Series(dtype='str'),
       'Medical Detail':pd.Series(dtype=str),
       'Results':pd.Series(dtype='str'),
       #'Doctor':pd.Series(dtype='str')
       
    })

    st.data_editor(st.session_state.datas,
      key='lab_history')


st.sidebar.header('Lab Panel')

if st.sidebar.button('🆕Lab sheet'):
    st.session_state.active_page='New'


if st.sidebar.button('History🏛️'):
    st.session_state.active_page='History'

    rows,err = lab_hist()
    if err:
         st.error(f"Network error:{err}")

    else:
       
      st.session_state.datas=pd.DataFrame(rows) if rows else pd.DataFrame()
      st.session_state.active_page='History'


if st.session_state.active_page=='New':
    stage1()


if st.session_state.active_page=='History':
    stage2()


else:
   st.info('👈 SELECT FROM THE SIDEBAR MENU')  