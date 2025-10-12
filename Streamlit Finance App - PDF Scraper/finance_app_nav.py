import streamlit as st 


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
    
def login():
    st.title("User Login")
    user = st.text_input("Enter Username:").lower()
    pw = st.text_input("Enter Password:")
    
    usernames = ['jose']
    pws = ['1234']
     
    if st.button("Sign In"):
        if (user in usernames) & (pw in pws):
            st.session_state.logged_in = True
            st.success("Success")
            st.rerun()
        else:
            st.error("Invalid Login")
        
def logout():
    st.title("Sign Out")
    if st.button("Sign Out"):
        st.session_state.logged_in = False
        st.rerun()

login_pg = st.Page(login, title="Log in", icon=":material/login:")
logout_pg = st.Page(logout, title="Log out", icon=":material/logout:")
main_pg = st.Page("finance_app_main.py",title="Home",default=True,icon=":material/home:")
budget_pg = st.Page("finance_app_budget.py",title="Budget",icon=":material/savings:")

if st.session_state.logged_in:
    pg = st.navigation({
        "Main":[main_pg],
        "Budget": [budget_pg],
        "Sign Out": [logout_pg]
        
        
        })
else:
     pg = st.navigation([login_pg])
     

pg.run()
