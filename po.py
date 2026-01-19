# ... (imports and global variables remain the same) ...

# ... (get_patient_names function as defined in the previous answer) ...
def get_patient_names():
    """
    Fetches all patient names from the doclab table to populate the selectbox options.
    """
    sql = "SELECT DISTINCT p_name FROM doclab ORDER BY p_name"
    try:
        with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = [row[0] for row in cur.fetchall()] # Extract just the names
                return rows, None
    except Exception as e:
        return None, str(e)


# New function to get details for a specific name
def get_patient_details(name):
    """
    Fetches the specific testing and medical details for the selected patient name.
    """
    sql = "SELECT testings, medical_d FROM doclab WHERE p_name = %s LIMIT 1"
    try:
        with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (name,))
                details = cur.fetchone()
                return details, None # Returns a dictionary or None
    except Exception as e:
        return None, str(e)


# The main stage1 function
def stage1():
    st.info('RESULTS FORM TO DOCTOR')

    names_list, err = get_patient_names()
    if err:
        st.error(f"Error fetching patient names: {err}")
        names_list = ["Error loading names"]
    if not names_list:
        names_list = ["No patients available"]

    # 1. Place the Selectbox OUTSIDE the form so it triggers a rerun immediately
    Select = st.selectbox('Select Name:', options=names_list, key='patient_select')

    # 2. Fetch details as soon as a new name is selected (triggered by the rerun)
    # The 'Select' variable holds the currently chosen name string
    details, details_err = get_patient_details(Select)
    
    # Set default values if details were fetched successfully
    default_testings = details['testings'] if details else "Details not found"
    default_medical_d = details['medical_d'] if details else "Details not found"


    # 3. Place the rest of the inputs INSIDE the form
    with st.form(key='from_doc', clear_on_submit=True):
        # Use the fetched details as the default value for the text areas
        # These fields are for the user to add *new* results/feedback
        st.text_area('Testings (from Doctor Request):', value=default_testings, height=100, disabled=True)
        st.text_area('Medical Details (from Doctor Request):', value=default_medical_d, height=150, disabled=True)
        
        # User input fields for the lab results
        ResuT = st.text_area('Lab Results (Fill this field):')
        
        Dname = st.selectbox('Doctor:', options=['Doctor1', 'Doctor2', 'Doctor3'])

        Submit = st.form_submit_button('Send Feedback')
        
        if Submit:
            if not ResuT:
                st.error('Please fill the Results field.')
            else:
                # Process submission using 'Select' (the patient name), 'ResuT' (lab results), and 'Dname'
                # Call update_lab_res() here with the relevant data
                st.success(f'✅Results sent Successfully for {Select}')
                # Example call (you need to define update_lab_res to take correct parameters)
                # ok, err = update_lab_res(ResuT, Select, default_testings)


# ... (stage2 function remains the same) ...
# ... (sidebar navigation remains the same) ...

if st.session_state.active_page == 'New':
    stage1()
elif st.session_state.active_page == 'History':
    stage2()
else:
   st.info('👈 SELECT FROM THE SIDEBAR MENU')

#########################################################################################
# ... (rest of stage1 code remains the same until the Submit button logic) ...

def stage1():
    # ... (code to fetch names and details as before) ...
    names_list, err = get_patient_names()
    # ... (error handling for names_list) ...

    Select = st.selectbox('Select Name:', options=names_list, key='patient_select')
    
    details, details_err = get_patient_details(Select)
    default_testings = details['testings'] if details else None
    default_medical_d = details['medical_d'] if details else None

    with st.form(key='from_doc', clear_on_submit=True):
        st.text_area('Testings (from Doctor Request):', value=default_testings, height=100, disabled=True)
        st.text_area('Medical Details (from Doctor Request):', value=default_medical_d, height=150, disabled=True)
        
        ResuT = st.text_area('Lab Results (Fill this field):')
        
        Dname = st.selectbox('Doctor:', options=['Doctor1', 'Doctor2', 'Doctor3'])

        Submit = st.form_submit_button('Send Feedback')
        
        if Submit:
            # Check if required fields are filled
            if not ResuT:
                st.error('Please fill the Lab Results field.')
            elif not default_testings:
                 st.error('Cannot send results; no testings were requested for this patient.')
            else:
                # Call the update function here
                success, error_message = update_lab_res(
                    lab_result=ResuT, 
                    patient_name=Select, 
                    testing_type=default_testings
                )
                
                if success:
                    st.success(f'✅Results sent Successfully for {Select}!')
                    # Optional: Rerun the script to clear the form visually after success
                    # st.rerun() 
                else:
                    st.error(f'❌Failed to send results. Error: {error_message}')

# ... (rest of your script) ...
##################################################################################################
def update_lab_res(lab_result, patient_name, testing_type):
    """
    Updates the doclab table with the lab results.
    """
    sql = """
       UPDATE doclab
       SET fromlabres = %s
       WHERE p_name = %s AND testings = %s
    """
    try:
        with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor() as cur:
                # Execute the update statement with the user input parameters
                cur.execute(sql, (lab_result, patient_name, testing_type))
                conn.commit() # Commit the transaction to save changes
        return True, None
    except Exception as e:
        return False, str(e)
