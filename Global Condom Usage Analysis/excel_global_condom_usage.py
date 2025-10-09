import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches

""" If the data shows as '...' then run the below set_option line, otherwise ignore it.
"""
pd.set_option('display.max_columns', None)

#Load Dataset
df = pd.read_csv(r'C:\Users\Jose\Documents\python\Rich_Global_Condom_Usage_Dataset.csv')

#Basic Information
print(f'This Dataset contains {df.shape[0]} rows and {df.shape[1]} columns')
print('Missing or Empty Values for each column:\n',df.isnull().sum())
round(df.describe(),1)

#Plotting the Charts from the Excel File
#Total Condom Sales by Country
ttl = df.groupby(["Country"])["Total Sales (Million Units)"].sum()
ttl = ttl.reset_index()
ttl['total_sales'] = ttl["Total Sales (Million Units)"].sum()
ttl["Total Sales %"] = ttl["Total Sales (Million Units)"] / ttl['total_sales']
ttl["Total Sales %"] = round(ttl["Total Sales %"],2)
def func(pct, data):
    #absolute = int(np.round(pct/100.*np.sum(data)))
    return f"{pct:.1f}%"

sns.set_palette("Paired")
plt.figure(figsize=(10,5))
plt.pie(ttl['Total Sales (Million Units)'],labels=ttl['Country'],autopct=lambda pct: func(pct,ttl['Total Sales (Million Units)']))
plt.title("Total Condom Sales by Country")
plt.legend(title="Country",bbox_to_anchor=(0,.6,0,0))
plt.show()

#Top Countries by Condom Sales
ttl = df.groupby(["Country"])["Total Sales (Million Units)"].sum()
ttl = ttl.reset_index()
ttl = ttl.sort_values(by="Total Sales (Million Units)",ascending=False).reset_index(drop=True)
sns.set_palette('tab10')
ax = sns.barplot(data=ttl,x="Total Sales (Million Units)",y='Country',width=.8)
ax.bar_label(ax.containers[0],fontsize=10);

#Most Popular Condom Types Worldwide
pop_type = df.groupby(["Most Popular Condom Type"])["Most Popular Condom Type"].count()
pop_type = pop_type.rename("Most Popular Condom Type Count")
pop_type = pop_type.reset_index()
pop_type = pop_type.sort_values(by="Most Popular Condom Type Count",ascending=False).reset_index(drop=True)
ax = sns.barplot(data=pop_type,x="Most Popular Condom Type Count",y='Most Popular Condom Type',width=.8)
ax.bar_label(ax.containers[0],fontsize=10);

#Male vs Female Condom Purchases by Country
#cleaning the data
mf = df[['Country','Male vs Female Purchases (%)']]
mf['split'] = mf['Male vs Female Purchases (%)'].str.split('-')
mf['male_percent'] = mf['split'].str[0]
mf['female_percent'] = mf['split'].str[1]
mf['male_percent'] = mf['male_percent'].str[:2]
mf['female_percent'] = mf['female_percent'].str[:3] 
mf['female_percent'] = mf['female_percent'].str.strip() 
mf['male_percent'] = "." + mf['male_percent']
mf['female_percent'] = "." + mf['female_percent']
mf['male_percent'] = pd.to_numeric(mf['male_percent'])
mf['female_percent'] = pd.to_numeric(mf['female_percent'])
mf = mf[['Country','male_percent','female_percent']]

#plotting the stacked bar chart
sns.set_palette('tab10')
plt.figure(figsize=(10,10))
bar1 = sns.barplot(x=mf['Country'],y=mf['male_percent'],data=mf,color="darkblue")
bar2 = sns.barplot(x=mf['Country'],y=mf['female_percent'],data=mf,color="lightblue")
topbar = mpatches.Patch(color='darkblue',label='Male')
bottombar = mpatches.Patch(color='lightblue',label='Female')
plt.legend(handles=[topbar,bottombar])
plt.show()

#Re-creating the Pivots tab from the Excel file
#Total Sales(Million Units) Year over Year and Growth YOY by Country
pvt = df[['Year','Country','Total Sales (Million Units)']]
pvt = pvt.pivot_table(index='Country',columns='Year',values='Total Sales (Million Units)',aggfunc='sum')
pvt = pvt.sort_values('Country',ascending=False)
for i in pvt.columns:
    fy = i
    if i < 2025:
        ny = i+1
        pvt[f'{fy} to {ny}'] = (pvt[ny] - pvt[fy]) / pvt[fy]

#Market Revenue (Million USD) YOY and Growth YOY by Country
pvt2 = df[['Year','Country','Market Revenue (Million USD)']]
pvt2 = pvt2.pivot_table(index='Country',columns='Year',values='Market Revenue (Million USD)',aggfunc='sum')
pvt2 = pvt2.sort_values('Country',ascending=False)
for i in pvt2.columns:
    fy = i
    if i < 2025:
        ny = i+1
        pvt2[f'{fy} to {ny}'] = (pvt2[ny] - pvt2[fy]) / pvt2[fy]

#Total Sales(Million Units) Year over Year and Growth YOY for Most Popular Condom Type
pvt3 = df[['Year','Most Popular Condom Type','Total Sales (Million Units)']]
pvt3 = pvt3.pivot_table(index='Most Popular Condom Type',columns='Year',values='Total Sales (Million Units)',aggfunc='sum')
pvt3 = pvt3.sort_values('Most Popular Condom Type',ascending=False)
for i in pvt3.columns:
    fy = i
    if i < 2025:
        ny = i+1
        pvt3[f'{fy} to {ny}'] = (pvt3[ny] - pvt3[fy]) / pvt3[fy]

