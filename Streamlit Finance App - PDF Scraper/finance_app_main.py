import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import datetime

st.set_page_config(page_title="Home", page_icon="🌤️", layout="wide")

category_file = "categories.json"
file_path = 'full_combined.csv'

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": [],
    }
    
if os.path.exists(category_file):
    with open(category_file, "r") as f:
        st.session_state.categories = json.load(f)
        
def save_categories():
    with open(category_file, "w") as f:
        json.dump(st.session_state.categories, f)

def categorize_transactions(df):
    df["Category"] = "Uncategorized"
    
    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue
        
        lowered_keywords = [keyword.lower().strip() for keyword in keywords]
        
        for idx, row in df.iterrows():
            details = row["Description"].lower().strip()
            if details in lowered_keywords:
                df.at[idx, "Category"] = category
                
    return df  

def load_transactions(file):
    try:
        df = pd.read_csv(file)
        df['Check Number'] = df['Check Number'].fillna(0)
        df['date_col'] = pd.to_datetime(df['Date'],format="%m/%d/%Y") 
        df['month_year'] = df['month_year'].str.replace("/","-")
        df['monthnum_year'] = df['date_col'].dt.strftime("%m-%Y")  
              
 
        
        return categorize_transactions(df)
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True
    
    return False

def main():
    st.title("Jose's Finance App")
    
    df = load_transactions(file_path)
    st.session_state["full_data"] = df.copy()
        
    if df is not None:
        debits_df = df[(df['Withdrawals/ Subtractions'] > 0)].copy()
        credits_df = df[(df['Deposits/Additions'] > 0)].copy()
        
        st.session_state.debits_df = debits_df.copy()
        
        tab1, tab2 = st.tabs(["Expenses", "Payments"])
        with tab1:
            new_category = st.text_input("New Category Name")
            add_button = st.button("Add Category")
            
            if add_button and new_category:
                if new_category not in st.session_state.categories:
                    st.session_state.categories[new_category] = []
                    save_categories()
                    st.rerun()
            
            st.subheader("Your Expenses")
            edited_df = st.data_editor(
                st.session_state.debits_df[["Date","Check Number","Description","Withdrawals/ Subtractions","user_account","month_year","monthnum_year","Category"]],
                column_config={
                    "Withdrawals/ Subtractions": st.column_config.NumberColumn("Withdrawals/ Subtractions", format="%.2f USD"),
                    "Category": st.column_config.SelectboxColumn(
                        "Category",
                        options=list(st.session_state.categories.keys())
                    )
                },
                hide_index=True,
                use_container_width=True,
                key="category_editor"
            )
            
            save_button = st.button("Apply Changes", type="primary")
            if save_button:
                for idx, row in edited_df.iterrows():
                    new_category = row["Category"]
                    if new_category == st.session_state.debits_df.at[idx, "Category"]:
                        continue
                    
                    details = row["Description"]
                    st.session_state.debits_df.at[idx, "Category"] = new_category
                    add_keyword_to_category(new_category, details)
                    
            st.subheader('Expense Summary')
            category_totals = st.session_state.debits_df.groupby(["monthnum_year","Category"])["Withdrawals/ Subtractions"].sum().reset_index()
            category_totals = category_totals.sort_values("monthnum_year", ascending=False)
            
            st.dataframe(
                category_totals, 
                column_config={
                    "Withdrawals/ Subtractions": st.column_config.NumberColumn("Withdrawals/ Subtractions", format="%.2f USD")   
                },
                use_container_width=True,
                hide_index=True
            )
            fig_data = category_totals.sort_values("monthnum_year", ascending=True).copy()
            fig = px.bar(fig_data,x="monthnum_year",y="Withdrawals/ Subtractions",color="Category")
            
            st.plotly_chart(fig,theme=None)

            
        with tab2:
            st.subheader("Payments Summary")
            total_payments = credits_df.groupby(["user_account","month_year"])["Deposits/Additions"].sum().reset_index()
            #this month this year
            tm_ty = datetime.datetime.now().strftime("%b") + "-" + datetime.datetime.now().strftime("%Y")
            j_tm_ty = total_payments[(total_payments['month_year'] == tm_ty) &
                                     (total_payments['user_account'] == "jose")]['Deposits/Additions'].sum()
            
            st.metric("Total Payments for this month(Jose)", f"{j_tm_ty:,.2f} USD")
            st.dataframe(credits_df[["Date","Description","Deposits/Additions","user_account"]],
                         column_config={"Deposits/Additions": st.column_config.NumberColumn("Deposits/Additions", format="%.2f USD") },
                         hide_index=True)
            
main()    