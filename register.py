# ...existing code...
import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import date

# Use environment var if available; fallback to the literal you had (recommended: move secret to .env)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.wegsxzwhrdhqsvkuqweg:codexhusseinmartinnkya@aws-1-eu-central-1.pooler.supabase.com:5432/postgres",
)

st.title("Patient Registration Sheet 🏥")

if "active_page" not in st.session_state:
    st.session_state.active_page = None

# initialize history DataFrame
if "datas" not in st.session_state:
    st.session_state.datas = pd.DataFrame(
        {
            "Reg_No": pd.Series(dtype="str"),
            "Name": pd.Series(dtype="str"),
            "Age": pd.Series(dtype="int"),
            "Sex": pd.Series(dtype="str"),
            "Contact": pd.Series(dtype="str"),
            "Address": pd.Series(dtype="str"),
            "Register_Date": pd.Series(dtype="datetime64[ns]"),
            "Doctor": pd.Series(dtype="str"),
        }
    )


def insert_patient_to_db(values_tuple):
    """
    Insert one patient row using a parameterized query.
    Uses a context manager so connection/cursor are closed automatically.
    """
    sql = """
    INSERT INTO hospital1 (reg_no, p_name, age, sex, contact, address, dname_reg, reg_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        # Using sslmode="require" for Supabase
        with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values_tuple)
                # conn.commit() is automatic when using with-block unless an exception occurs
        return True, None
    except Exception as e:
        return False, str(e)


def add_patient():
    # Build form and collect values only when submitted
    with st.form(key="register_patient_form", clear_on_submit=True):
        Reg_no = st.text_input("Registration Number:")
        Name = st.text_input("Patient Name:")
        Age = st.number_input("Age:", min_value=0, max_value=120, step=1)
        Gender = st.selectbox("Sex:", ["Male", "Female"])
        Contact = st.text_input("Contact:")
        Address = st.text_input("Address🕵️:")
        Doctor = st.selectbox(
            "Doctor to consults👨🏻‍⚕️:", ["Doctor1", "Doctor2", "Doctor3", "Doctor4"]
        )
        Register = st.date_input("Registration Date:", value=date.today())
        Submit = st.form_submit_button("Submit")

    if Submit:
        # Basic validation
        if not (Reg_no and Name and Contact):
            st.error("Fill all required fields")
            return

        # Prepare tuple in the same order as the SQL statement
        values = (
            Reg_no,
            Name,
            int(Age),
            Gender,
            Contact,
            Address,
            Doctor,
            Register,  # psycopg2 accepts datetime.date
        )

        ok, err = insert_patient_to_db(values)
        #err='Fail to Submit Due to internet difficulties'
        if ok:
            st.success(f"✅ {Name} record successfully added!")
            # append to local session history so the UI updates immediately
            st.session_state.datas = pd.concat(
                [
                    st.session_state.datas,
                    pd.DataFrame(
                        {
                            "Reg_No": [Reg_no],
                            "Name": [Name],
                            "Age": [int(Age)],
                            "Sex": [Gender],
                            "Contact": [Contact],
                            "Address": [Address],
                            "Register_Date": [pd.to_datetime(Register)],
                            "Doctor": [Doctor],
                        }
                    ),
                ],
                ignore_index=True,
            )
        else:
            st.error(f"Memory error: {err}")


def fetch_all_patients():
    """
    Return list of dicts for all patients (or None, error).
    """
    sql = """
    SELECT reg_no, p_name, age, sex, contact, address, dname_reg, reg_date
    FROM hospital1
    ORDER BY reg_date DESC NULLS LAST
    """
    try:
        with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                return rows, None
    except Exception as e:
        return None, str(e)



def level1():
    st.info("History Details📜")

   
    
    st.data_editor(st.session_state.datas, key="doctor_data_editor")
    

st.sidebar.header("Registration Panel 🏥")

if st.sidebar.button("➕New Patient"):
    st.session_state.active_page = "New patient"

if st.sidebar.button("History📜"):
    rows, err = fetch_all_patients()
    if err:
        st.error(f"Network fail:{err}")
    else:

      st.session_state.datas = pd.DataFrame(rows) if rows else pd.DataFrame()
      st.session_state.active_page = "History"

if st.session_state.active_page == "New patient":
    add_patient()
elif st.session_state.active_page == "History":
    level1()
else:
    st.info("👈 SELECT FROM THE SIDEBAR MENU")
# ...existing code...