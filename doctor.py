import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.wegsxzwhrdhqsvkuqweg:codexhusseinmartinnkya@aws-1-eu-central-1.pooler.supabase.com:5432/postgres",
)

st.header('DOCTOR SHEET')

 


if 'active_page' not in st.session_state:
   st.session_state.active_page=None

if 'datas' not in st.session_state:
  st.session_state.datas=pd.DataFrame({
         'Name':pd.Series(dtype='str'),
         'Age':pd.Series(dtype='int'),
         'Sex':pd.Series(dtype=str),
         'Doctor':pd.Series(dtype='str')
   })
   






def get_pnames():#get patients names
   sql="""
       SELECT DISTINCT p_name FROM hospital1 
"""
   
   try:
      with psycopg2.connect(DATABASE_URL,sslmode="require") as conn:
         with conn.cursor() as cur:
            cur.execute(sql)

            rows=[row[0] for row in cur.fetchall() ]
            return rows,None
   except Exception as e:
      return None,str(e)
   

def add_details(name):
   sql="""

       SELECT age,sex,testings,dname_reg FROM hospital1 WHERE p_name=%s LIMIT 1 
"""

   try:
      with psycopg2.connect(DATABASE_URL,sslmode='require') as conn:
         with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql,(name,))
            details=cur.fetchone()
            return details,None
   except Exception as e:
      return None,str(e)


def details_lab(testings,medical_det,p_name):
   sql="""
   UPDATE hospital1
   SET testings=%s,medical_det=%s
   WHERE p_name=%s 
   
"""
   
   try:
      with psycopg2.connect(DATABASE_URL,sslmode='require') as conn:
         with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql,(testings,medical_det,p_name))
            return True,None  
   except Exception as e:
      return None,str(e)

def fetch_all_patients():
    """
    Return list of dicts for all patients (or None, error).
    """
    sql = """
    SELECT p_name, age, sex, contact, testings, dname_reg, medical_det
    FROM hospital1
    ORDER BY p_name DESC NULLS LAST
    """
    try:
        with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                return rows, None
    except Exception as e:
        return None, str(e)




def view_lab_res(name):
   sql="""
  SELECT testings,testres FROM hospital1 WHERE p_name=%s LIMIT 1
"""
   try:

    with psycopg2.connect(DATABASE_URL,sslmode='require') as conn:
      with conn.cursor(cursor_factory=RealDictCursor) as cur:
         cur.execute(sql,(name,))
         rows=cur.fetchone()
         return rows,None
   except Exception as e:
      return None,str(e)

def step1():
  
  st.info('SEND PATIENT DETAILS TO LAB')
  Select_name,err=get_pnames()
  if err:
     st.error(f'Fail to get names:{err}')
     Select_name=['Error loading names']

  if not Select_name:
     Select_name=['No patients record available']

  Choose=st.selectbox('Select Patient Names:',options=Select_name)
   
  details,details_err=add_details(Choose)
  details_age=details.get('age' )
  details_sex=details.get('sex')
  details_dname=details.get('dname_reg')
 

   
  

  
  with st.form(key='doctor_form',clear_on_submit=True):
  #this are suppose to run on the relation from the registration 
   
  
   Age=st.text_input('Age:',value=details_age)
   sex=st.text_input('Sex:',value=details_sex)
   testings=st.multiselect('Testings:',['Blood Test🩸','Urinalysis','Biopsy','X-ray🩻','MRI','CT-scan','Ultrasound'])
   Dname=st.text_input('Doctor Name:',value=details_dname)
   Medical=st.text_area('Medical Details:')
   Submit=st.form_submit_button('Send to 🧪')
  
   
   
   if Submit:
      
    if not all([Medical.strip()]):
            st.error("Fill all required fields ( Name, Contact, Medical)")


    values=[testings,Medical,Choose]
    ok,err=details_lab(testings,Medical,Choose)

    if ok:
       st.success(f'✅{Choose} Details Sent Successfull to Lab')
            
    else:
         st.error(f'Error sending to lab:{err}')
      

def step2():
    
    st.info('LAB HISTORY')
    

    st.session_state.datas=pd.DataFrame({
       'Name':pd.Series(dtype='str'),
       'Age':pd.Series(dtype='int'),
       'Sex':pd.Series(dtype=str),
       'Testings':pd.Series(dtype=str),
       'Medical_details':pd.Series(dtype=str)
       
    })

    st.data_editor(st.session_state.datas,
      key='doctor_data_editor')
    
def step3():
  
  st.info('VIEW RESULT FROM LAB')
  det,err=get_pnames()
  if err:
     st.error(f'Fail to load name')
     det=['Error to load']

  Select=st.selectbox('Select Name:',options=det)


  view,err=view_lab_res(Select)
  if err:
     st.error(f'Error to load data')
  v_testings=view.get('testings','')
  v_results=view.get('testres','')


   
  if isinstance(v_testings, list):
        v_testings = ", ".join(v_testings)




  with st.form(key='labres_form',clear_on_submit=True):
        
        TesT=st.text_area('Testings Diagnosed:',value=v_testings,width=400,height=150)
        ResuT=st.text_area('Results Diagnosed:',value=v_results)
    
        #Submit=st.form_submit_button('Clear')
        
def step4():
    st.info('Send the Results to pharmacy')
    Namer=st.text_input('patient Name:')

    with st.form(key='doctor_lab',clear_on_submit=True):
     
     Details=st.text_area('Medical Details:')
     Doctore=st.selectbox('Doctor Name:')
     Confirm=st.checkbox('Confirm Details are correct')
     Send=st.form_submit_button('Send to Pharmacy💊')


     if Send:
        
        if not Details.strip():
          st.error('Fill All the Field')
        elif not Namer:
          st.error('Fill All The Field')
        elif not Doctore:
          st.error('Fill All The Field')


        datam=[Namer,Details,Doctore]
      
        ok, err = insert_to_pham(datam)
        if ok:
              st.success(f'✅{Namer} Details Sent Successfull to Pharmacy')
        else:
              st.error(f"Network error:{err}")

     #elif Namer is None:
       # st.error('Select the Patient Name')  
     #elif Doctorer is None:
      #  st.error('Select the Doctor Name')

     #elif Details.strip():
      #  st.error('Fill the Patients Details')   

     #elif Submit and Confirm is None:
      #  st.error ('Confirm before Submit')
          
def insert_to_pham(data):
   sql="""
       INSERT INTO hospital1 WHERE p_name=%s,medical=%s,dname=%s
      
"""

   try:
         with psycopg2.connect(DATABASE_URL,sslmode="require") as conn:
            with conn.cursor() as cur:
               cur.execute(sql,data)
         return True,None
   except Exception as e:
        return False,str(e)

   

def insert_to_lab(values_tuple):
    sql='''
    INSERT INTO doclab(p_name,age,sex,testings,dname,medical_d)
    VALUES(%s,%s,%s,%s,%s,%s)
 '''
    
    try:
        # Using sslmode="require" for Supabase
        with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values_tuple)
                # conn.commit() is automatic when using with-block unless an exception occurs
        return True, None
    except Exception as e:
        return False, str(e)


st.sidebar.header('Doctor Panel🩺')
   

if st.sidebar.button('Patient to Lab🧪'):
   st.session_state.active_page='to_lab'

if st.sidebar.button('Lab History🔬'):
   st.session_state.active_page='from_lab'

   rows, err = fetch_all_patients()
   if err:
        st.error(f"Network error:{err}")
   else:

      st.session_state.datas = pd.DataFrame(rows) if rows else pd.DataFrame()
      st.session_state.active_page = "from_lab"


if st.sidebar.button('View Results'):
  st.session_state.active_page='View_Results' 

if st.sidebar.button('To Pharmacy💊'):
   st.session_state.active_page='to_pharmacy' 


   

if st.session_state.active_page=='to_lab':
   step1()
   
   
if st.session_state.active_page=='from_lab':
   step2()      

if st.session_state.active_page=='View_Results':
  step3()

if st.session_state.active_page=='to_pharmacy':
   step4()


else:
   st.info('👈 SELECT FROM THE SIDEBAR MENU')  