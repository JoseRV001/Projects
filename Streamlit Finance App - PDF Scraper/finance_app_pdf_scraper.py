from PyPDF2 import PdfReader as pdfreader
import PyPDF2
import pandas as pd
import re
import os
import datetime
from datetime import timedelta
import time 

#Establishing pdf path to be read in
pdf_path = r"Jose WellsFargo Edited.pdf"

#pdf_text is the list we'll use to extract the data from the pdf
pdf_text = []
with open(pdf_path,'rb') as pdf:
     reader = pdfreader(pdf,strict=False)
     
     for page in reader.pages:
         content = page.extract_text()
         pdf_text.append(content)
         
#Only grabbing the transactions, we dont want anything else
pdf_text2 = []
for i in range(len(pdf_text)):
    if 'transaction history' in pdf_text[i].lower():
        begin_num = pdf_text[i].lower().find('transaction history')
        end_num = pdf_text[i].lower().find('totals')
        if end_num > 0:
            actual_data = pdf_text[i][begin_num :end_num]
        else:
            #print('End of transaction not found')
            actual_data = pdf_text[i][begin_num :]
        pdf_text2.append(actual_data)

#After grabbing only transactions, we realize that the transactions continue on a page with only account information
#So re-scrape the pdf text again
pdf_text3 = []
for i in range(len(pdf_text2)):
    if 'IMPORTANT ACCOUNT INFORMATION' in pdf_text2[i]:
        pass
    else:
        begin_num = pdf_text2[i].lower().find('balance')
        begin_num = begin_num + len('balance') +2
        actual_data = pdf_text2[i][begin_num :]
        pdf_text3.append(actual_data)

#list comp to parse out text for each line break
split_text = [element.split(sep='\n') for i,element in enumerate(pdf_text3)]
#list comp to flatten out nested list
split_text = [element for innerList in split_text for element in innerList]
#removing any empty objects
split_text = [item for item in split_text if len(item) > 0]

#Iterate thru the split text to restablish the transactions lines for readability
corr_list = []
corr_list_index = []
#Looks in each list object to find the date and establishes the "line"
for i in range(len(split_text)):
    if re.search("(\d{1,2}[/]\d{1,2}[/]\d{2,4})", split_text[i]) is not None:
        new_string = split_text[i-1] + split_text[i]
        corr_list.append(new_string)
        corr_list_index.append(i-1)
        corr_list_index.append(i)
        
    if "/" not in split_text[i]:
        new_string = split_text[i-1] + split_text[i]
        corr_list.append(new_string)
        corr_list_index.append(i-1)
        corr_list_index.append(i)

#Grabs the excluded items from above
x_list = [element for i,element in enumerate(split_text) if i not in corr_list_index]
#Joins the two lists back together
final_list = corr_list + x_list

#There are still two list objects not properly lined up so we re-iterate
corr_list = []
corr_list_index = []

for i,element in enumerate(final_list):
    if "/" not in element:
        new_string = final_list[i-1] + final_list[i]
        corr_list.append(new_string)
        corr_list_index.append(i-1)
        corr_list_index.append(i)
    
    if "Amzn.Com/Bill" in element:
        new_string = final_list[i-1] + final_list[i]
        corr_list.append(new_string)
        corr_list_index.append(i-1)
        corr_list_index.append(i)

#list comp to grab the lists not appended
x_list = [element for i,element in enumerate(final_list) if i not in corr_list_index]
#joins the twol lists back together
final_list = corr_list + x_list

#Now that every trasancation has been lined up, now get the data ready for a dataframe
#Most of the transactions follow the same format except for the check
final_split_list = []
#the check goes into its own list since it has a different format
check_split_list = []
#dep_add_strings are the transactions descriptions that are additions rather than subtractions/withdrawals
dep_add_strings = ['Job Payment','Zelle From']

for i,element in enumerate(final_list):
    x = re.search(r"\d{3,4}\s", final_list[i])
    y = re.search(r"check\s", final_list[i],re.IGNORECASE)
    if x and y:
        #print(i)
        split_text = re.split(r"  ",final_list[i])
        check_split_list.append(split_text)
    elif 'Hot Topic Payrollach' in element or 'Zelle From' in element:
        #print(i)
        split_text = re.split(r"  ",final_list[i])
        final_split_list.append(split_text)
        
    else:
        split_text = re.split(r"   ",final_list[i])
        final_split_list.append(split_text)

#dt for Date, chk_num for Check Number, desc for Description
#dep_add for Deposits/Additions, with_subt for Withdrawals/Subtractions
dt = []
chk_num = []
desc = []
dep_add = []
with_subt = []

#Removing the blank objects from each of the nested list 
for i,element in enumerate(final_split_list):
    for ii,ee in enumerate(element):
        if len(ee) <=1:
            element.pop(ii)

for i,element in enumerate(check_split_list):
    for ii,ee in enumerate(element):
        if len(ee) <=1:
            element.pop(ii)
            
#Adding each of the objects from the nested lists into their respective list 
#This is how we'll form the dataframe
for i,element in enumerate(final_split_list):
    dt_str = final_split_list[i][0]
    dt.append(dt_str)
    chk_num.append("")
    pdf_desc = final_split_list[i][1]
    desc.append(pdf_desc)
    if any(item in pdf_desc for item in dep_add_strings):
        #print(i)
        da_str = final_split_list[i][2]
        dep_add.append(da_str)
        with_subt.append("")
    else:
        dep_add.append("")
        ws_str = final_split_list[i][2]
        with_subt.append(ws_str)

for i,element in enumerate(check_split_list):
    dt_str = check_split_list[i][0]
    dt.append(dt_str)
    ck_n = check_split_list[i][1]
    chk_num.append(ck_n)
    pdf_desc = check_split_list[i][2]
    desc.append(pdf_desc)
    dep_add.append("")
    ws_str = check_split_list[i][3]
    with_subt.append(ws_str)

#Column names for dataframe
col_names = ['Date','Check Number','Description','Deposits/Additions','Withdrawals/ Subtractions']
#Forming the dataframe with all of the now added lists
data = {col_names[0] : dt,
        col_names[1] : chk_num,
        col_names[2] : desc,
        col_names[3] : dep_add,
        col_names[4] : with_subt,
        }

df = pd.DataFrame(data)
#Adding year and cleaning the Date column
df['Date'] = df['Date'] + '/2025'
df['Date'] = df['Date'].str.strip()
df['date_col'] = pd.to_datetime(df['Date'],format='%m/%d/%Y',errors='coerce')
df.sort_values(by=['date_col'],inplace=True)
df.reset_index(drop=True,inplace=True)
df['month_year'] = df['date_col'].dt.strftime("%b/%Y")
float_cols = ['Deposits/Additions','Withdrawals/ Subtractions']
for col in df.columns:
    if col in float_cols:
        df[col] = df[col].map(str.strip)
        df[col] = df[col].str.replace(",","")
        df[col] = pd.to_numeric(df[col],errors='coerce')
        df[col] = df[col].fillna(0)
        df[col] = df[col].astype('float')
df['total_withd_subt_by_month'] = df.groupby(['month_year'])['Withdrawals/ Subtractions'].transform('sum')
df['user_account'] = 'jose'
df.to_csv('\\tranasaction_data.csv',index=False)
