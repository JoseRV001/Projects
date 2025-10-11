import streamlit as st 
import datetime
from datetime import timedelta
import json
import os
import pandas as pd

budget_file = "budget_transactions.json"

if "transactions" not in st.session_state:
    st.session_state.transactions = []
    
if os.path.exists(budget_file):
    with open(budget_file, "r") as f:
        st.session_state.transactions = json.load(f)
else:
    pass

def save_transactions():
    with open(budget_file, "w") as f:
        json.dump(st.session_state.transactions, f)

def add_transaction(n,d,a,c):
    n = n.strip()
    d = d.strip()
    a = str(a).strip()
    c = c.strip()
    trans_dict = {"Name":n,"Description":d,"Amount":a,"Category":c}
    st.session_state.transactions.append(trans_dict)
    save_transactions()



def budget():
    st.title("Jose Budget")
    
    df = st.session_state["full_data"]
    jose_df = df[df['user_account']=='jose']
    ttl = df.groupby(['monthnum_year','month_year'])["Deposits/Additions"].sum().reset_index()
    j_ttl = jose_df.groupby(['monthnum_year','month_year'])["Deposits/Additions"].sum().reset_index()
    ttl = ttl.sort_values("monthnum_year",ascending=False).reset_index(drop=True)
    j_ttl = j_ttl.sort_values("monthnum_year",ascending=False).reset_index(drop=True)
    delta = timedelta(days=-30)
    today = datetime.datetime.now()
    lm = today + delta
    lm_ty = lm.strftime("%b") + "-" + datetime.datetime.now().strftime("%Y")
    tm_ty = datetime.datetime.now().strftime("%b") + "-" + datetime.datetime.now().strftime("%Y")
    lm_ttl = ttl[(ttl["month_year"] == lm_ty)]["Deposits/Additions"].reset_index(drop=True)
    ttl = ttl[(ttl["month_year"] == tm_ty)]["Deposits/Additions"].reset_index(drop=True)
    lm_ttl = lm_ttl[0]
    
    if ttl.empty:
        st.badge("Using Last Month Data",icon=":material/e911_emergency:",color="red")
        ttl = lm_ttl
        tm_ty = lm_ty
    elif ttl.empty and lm_ttl.empty:
        st.write("Something went wrong")
    else:
        st.badge("Using This Month Data",color="green")
        ttl = ttl[0]
    
    j_ttl = j_ttl[(j_ttl["month_year"] == tm_ty)]["Deposits/Additions"].reset_index(drop=True)
    j_ttl = j_ttl[0]
    col1,col2,col3 = st.columns(3)
    col1.metric("Total Payments for Jose This Month", f"{j_ttl:,.2f} USD")
    col3.metric("Total Payments for Both This Month", f"{ttl:,.2f} USD")
    
    with st.form("combined_form"):
        st.header("Add Transaction")
        subheader = st.columns(4)
        subheader[0].subheader("Name")
        subheader[1].subheader("Description")
        subheader[2].subheader("Amount")
        subheader[3].subheader("Category")
        
        #inputs
        inputs = st.columns(4)
        name = inputs[0].selectbox(label="Name",options=["jose"])
        desc = inputs[1].text_input(label="Description")
        amt = inputs[2].number_input(label="Amount")
        cat = inputs[3].selectbox(label="Category",options=list(st.session_state.categories.keys()))
        
        submit = st.form_submit_button(label="Add Transaction")
        if submit:
            st.success("Transaction Added")
            add_transaction(name, desc, amt, cat)
            st.rerun()
            
    n = .5
    w = .3
    sd =.2
            
    
    st.header("Needs")  
    try:
        df = pd.DataFrame(st.session_state.transactions)
        needs = ["Groceries","Rent","Gasoline"]
        n_df = df[df["Category"].isin(needs)].copy()
        st.dataframe(n_df)
        n_ttl_amt = n_df["Amount"].sum()
        jn_df = n_df[n_df['Name'] == "jose"]
        st.write("Total Spent:",f"{n_ttl_amt} USD","Total Amount Left:",f"{(ttl*n)-n_ttl_amt} USD")
    except Exception as e:
        st.badge("No transactions yet",color="green")
    
    
    st.header("Wants")  
    try:
        df = pd.DataFrame(st.session_state.transactions)
        w_df = df[~df["Category"].isin(needs)]
        st.dataframe(w_df)
        w_ttl_amt = w_df["Amount"].sum()
        st.write("Total Spent:",f"{w_ttl_amt} USD")
    except Exception as e:
        st.badge("No transactions yet",color="green")
        
    
    st.header("Savings & Debt Repayment")  
    try:
        df = pd.DataFrame(st.session_state.transactions)
        s_d = ["Bank Fees"]
        sd_df = df[df["Category"].isin(s_d)]
        st.dataframe(sd_df)
        sd_ttl_amt = sd_df["Amount"].sum()
        st.write("Total Spent:",f"{sd_ttl_amt} USD")
    except Exception as e:
        st.badge("No transactions yet",color="green")
        
        
        
        
        
        
    
    
    
    

def main():
    if "full_data" not in st.session_state:
        st.write("something went wrong!")
        
    else:
        budget()

main()