# ...existing code...
import streamlit as st

st.set_page_config(page_title='Hospital Management system', page_icon='🏨')

# Simple user store (replace with real auth / DB in production)
accounts = {
    "reguser":    {"password": "reg", "role": "Register"},
    "doctor1":    {"password": "doc", "role": "Doctor"},
    "lab1":       {"password": "lab", "role": "Lab"},
    "pharm1":     {"password": "phar", "role": "Pharmacy"},
    "admin":      {"password": "123", "role": "Admin"},
}

# Which files each role can access
role_pages = {
    "Admin":     ["register.py", "doctor.py", "lab.py", "pharmacy.py"],
    "Register":  ["register.py"],
    "Doctor":    ["doctor.py"],
    "Lab":       ["lab.py"],
    "Pharmacy":  ["pharmacy.py"],
}

# Display metadata for pages
page_info = {
    "register.py":  ("Register page", "📝"),
    "doctor.py":    ("Doctor page", "👨‍⚕️"),
    "lab.py":       ("Lab page", "🔬"),
    "pharmacy.py":  ("Pharmacy page", "💊"),
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    username = st.text_input("Username:", key="username_input")
    password = st.text_input("Password:", type="password", key="password_input")

    if st.button("Login"):
        acct = accounts.get(username)
        if acct and acct["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = acct["role"]
            st.success(f"Logged in as {username} ({acct['role']})")
            st.rerun()
        else:
            st.error("⚠ Oops! Wrong credentials")

if st.session_state.logged_in:
    user_role = st.session_state.role
    allowed_files = role_pages.get(user_role, [])
    pages = []
    for f in allowed_files:
        title, icon = page_info.get(f, (f, "📄"))
        pages.append(st.Page(f, title=title, icon=icon))

    with st.sidebar:
        st.markdown(f"**User:** {st.session_state.username}")
        st.markdown(f"**Role:** {user_role}")
        if st.button("Logout", on_click=logout):
            logout()

    if not pages:
        st.warning("No pages available for your role.")
    else:
        pg = st.navigation(pages)
        pg.run()
# ...existing code...