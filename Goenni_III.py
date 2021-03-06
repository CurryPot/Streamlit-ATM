import glob
import os 
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import altair as alt
from vega_datasets import data
import datetime as dt
import pandas as pd
import openpyxl

today = dt.date.today()

CurrentWeek = int(today.isocalendar().week)

DATA_URL = (r"ATMweb.txt")
#DATA_URL = r"\\WNSAN01\Department\Logistic\22 - Seefracht\AMT\Input Data\web\ATMweb.txt"

data = pd.read_csv(DATA_URL, sep=",",header=None, index_col=False)

data = data.rename(columns={1:'Year',2:'Month',3:'Week',4:'POL',5:'Forwarder',6:'FC_Allocation/Week in TEU',
             7:'Confirmed_TEU',8:'ConfirmedBalance',9:'%ConfirmedTEU', 10:'Pipeline', 11:'PipelineBalance',12:'%Pipeline', 13:'Allocation/Week in TEU'})

data = data[['Year','Month','Week','POL','Forwarder','FC_Allocation/Week in TEU',
             'Confirmed_TEU','Pipeline','%Pipeline', 'Allocation/Week in TEU']]

data["chk"] = ""
for row in range(len(data)):
    if data.loc[row,'Year'] == 'Year':
        data.loc[row,"chk"] = "out"
    else:
        data.loc[row,"chk"] = "in"

#################################################################################################################################################

data = data[data["chk"] == "in"]

data = data[['Year','Month','Week','POL','Forwarder','FC_Allocation/Week in TEU',
             'Confirmed_TEU','Pipeline','%Pipeline', 'Allocation/Week in TEU']]

data = data.fillna('0')
data['Year'] = data['Year'].astype(float)
data['Year'] = data['Year'].astype(int)

data = data[data["Year"]!=0]

data['FC_Allocation/Week in TEU'] = data['FC_Allocation/Week in TEU'].fillna('0')
data['FC_Allocation/Week in TEU'] = data['FC_Allocation/Week in TEU'].astype(float)
data['FC_Allocation/Week in TEU'] = data['FC_Allocation/Week in TEU'].astype(int)

data['Allocation/Week in TEU'] = data['Allocation/Week in TEU'].fillna('0')
data['Allocation/Week in TEU'] = data['Allocation/Week in TEU'].astype(float)
data['Allocation/Week in TEU'] = data['Allocation/Week in TEU'].astype(int)

data['Pipeline'] = data['Pipeline'].fillna('0')
data['Pipeline'] = data['Pipeline'].astype(float)
data['Pipeline'] = data['Pipeline'].astype(int)

data['%Pipeline'] = data['%Pipeline'].fillna('0')
data['%Pipeline'] = data['%Pipeline'].astype(float)
data['%Pipeline'] = data['%Pipeline'].astype(int)

data['Confirmed_TEU'] = data['Confirmed_TEU'].fillna('0')
data['Confirmed_TEU'] = data['Confirmed_TEU'].astype(float)
data['Confirmed_TEU'] = data['Confirmed_TEU'].astype(int)

data["Week"] = data["Week"].fillna('0')
data["Week"] = data["Week"].astype(float)
data["Week"] = data["Week"].astype(int)

data["Month"] = data["Month"].fillna('0')                                                     
data["Month"] = data["Month"].astype(float)
data["Month"] = data["Month"].astype(int)

data = data.fillna(0)

data = data[data["POL"]!=None]
data = data[data["POL"]!="XXX"]
data = data[data["POL"]!=0]
data = data[data["Year"]!=0]
data = data[data["Month"]>5]

data_allo = data.copy()
data_allo["Type"] = "Allo"
data_allo = data_allo[["Year", "Month", "Week", "POL", "Forwarder", "Type", "Allocation/Week in TEU"]]
data_allo = data_allo.rename(columns={"Allocation/Week in TEU":"TEU"})

data_allocation = data.copy()
data_allocation["Type"] = "Allocation"
data_allocation = data_allocation[["Year", "Month", "Week", "POL", "Forwarder", "Type", "FC_Allocation/Week in TEU"]]
data_allocation = data_allocation.rename(columns={"FC_Allocation/Week in TEU":"TEU"})

data_Pipeline = data.copy()
data_Pipeline["Type"] = "Pipeline"
data_Pipeline = data_Pipeline[["Year", "Month", "Week", "POL", "Forwarder", "Type","Pipeline"]]
data_Pipeline = data_Pipeline.rename(columns={"Pipeline":"TEU"})

data_confirmed = data.copy()
data_confirmed["Type"] = "Confirmed"
data_confirmed = data_confirmed[["Year", "Month", "Week", "POL", "Forwarder", "Type","Confirmed_TEU"]]
data_confirmed = data_confirmed.rename(columns={"Confirmed_TEU":"TEU"})

df_combined = pd.concat([data_allo, data_allocation,data_Pipeline, data_confirmed])
df_combined = df_combined[df_combined["Forwarder"] != 0]

v = df_combined.copy()
v = v[v["Type"]=="Allocation"]
v.reset_index(drop=True,inplace=True)
v = v.rename(columns={"TEU":"Allocation"})
v = v[["Year", "Month", "Week", "POL", "Forwarder","Type", "Allocation"]]

b = df_combined.copy()
b = b[b["Type"]=="Allo"]
b.reset_index(drop=True,inplace=True)
b = b.rename(columns={"TEU":"Allo"})
b = b[["Year", "Month", "Week", "POL", "Forwarder","Type", "Allo"]]

df_combined_II = pd.merge(df_combined, b,
                             on=["Year", "Month", "Week", "POL", "Forwarder", "Type"], how="left")


df_combined_final = pd.merge(df_combined_II, v,
                             on=["Year", "Month", "Week", "POL", "Forwarder", "Type"], how="left")

df_combined_final["Allocation"] = df_combined_final["Allocation"].fillna(0)
df_combined_final["Allocation"] = df_combined_final["Allocation"].astype(int)

df_combined_final["Allo"] = df_combined_final["Allo"].fillna(0)
df_combined_final["Allo"] = df_combined_final["Allo"].astype(int)

source = df_combined_final.copy()
sourceII = df_combined_final.copy()
SliderData = df_combined_final.copy()

#############################################################################################################################################
DEFAULT = '< PICK A VALUE >'

st.set_page_config(page_title= "Allocation Management Tool", 
                  page_icon = ":anchor:",
                  layout="wide")

st.sidebar.header("Filter Data Here:")

wk = source["Week"].unique()
wk_chk_list = wk.tolist()
wk_chk_list.append(0)
wk_chk_list = sorted(wk_chk_list)

Week = st.sidebar.selectbox("Select Week:", 
                            wk_chk_list)

if Week == 0:
	st.write("Select Week")
	
else:
	POL_chk = source[source["Week"] == Week] 

	x = POL_chk['POL'].unique()
	POL_chk_list = x.tolist()
	POL_chk_list.append(DEFAULT)
	POL_chk_list = sorted(POL_chk_list)
	

	POL =  st.sidebar.selectbox("Select POL:", POL_chk_list)
	
	if POL == DEFAULT:
		st.write("Select POL")
	else:
		FWD_chk = POL_chk[POL_chk["POL"] == POL] 

		x = FWD_chk['Forwarder'].unique()
		FWD_chk_list = x.tolist()
		FWD_chk_list.append(DEFAULT)
		FWD_chk_list = sorted(FWD_chk_list)
		
		Forwarder =  st.sidebar.selectbox("Select Forwarder:", FWD_chk_list)
		
		if Forwarder == DEFAULT:
			#--- Main Page ---
			df_selection = source.query("Week==@Week & POL==@POL")
			df_selection.reset_index(drop=True,inplace=True)
			
					
			per_of_total = df_selection.copy()
			
			
			per_of_totalII = per_of_total.pivot_table(index=["Year","Month","Week","POL","Forwarder"],
										  columns='Type', values='TEU', aggfunc='sum').reset_index()

			per_of_totalII["%Confirmed"] = per_of_totalII["Confirmed"] / per_of_totalII["Allocation"]
			per_of_totalII["%Pipeline"] = per_of_totalII["Pipeline"] / per_of_totalII["Allocation"]
			per_of_totalII = per_of_totalII.replace([np.inf, -np.inf], 0)
			per_of_totalII = per_of_totalII.rename_axis(None, axis=1)
			per_of_totalII = per_of_totalII.fillna(0)

			just_a_shot = per_of_totalII.copy()
			per_of_totalIIV1 = per_of_totalII.copy()

			per_of_totalIIV1 = per_of_totalIIV1[["Year","Month","Week","POL","Forwarder",
								   "Allocation","Confirmed","Pipeline"]]
								   
			per_of_totalIIV1 = pd.melt(per_of_totalIIV1, id_vars =["Year","Month","Week","POL","Forwarder"],
			value_vars =["Allocation","Confirmed","Pipeline"], var_name='Type', value_name='TEU')

			per_of_totalIIV2 = per_of_totalII.copy()

			per_of_totalIIV2 = per_of_totalIIV2[["Year","Month","Week","POL","Forwarder","%Confirmed","%Pipeline"]] 

			per_of_totalIIV2 = pd.melt(per_of_totalIIV2, id_vars =["Year","Month","Week","POL","Forwarder"],
						   value_vars =["%Confirmed","%Pipeline"], var_name='%Type', value_name='%Filled')

			per_of_totalIIV2["Type"] = np.where(per_of_totalIIV2["%Type"] == "%Confirmed", "Confirmed", "Pipeline")


			finalselection = pd.merge(per_of_totalIIV1, per_of_totalIIV2,
						  on=["Year","Month","Week","POL","Forwarder", "Type"],
						  how="outer")

			finalselection["%Type"] = np.where(finalselection["Type"] == "Allocation",
								   "Total Allocation",
								   finalselection["%Type"])																		

			finalselection["%Filled"] = np.where(finalselection["Type"] == "Allocation",
								   1,
								   finalselection["%Filled"])
								   
			finalselection['%Filled'] = round(finalselection['%Filled'], 2)
			
			st.title(":anchor: Port: "+str(df_selection.loc[0,"POL"]))
			st.subheader(":calendar: Week: "+str(df_selection.loc[0,"Week"]))
						
			bar_x = alt.Chart(finalselection, height=500, width={"step": 120}).mark_bar().encode(
				x='Type:O',
				y='TEU:Q',
				color='Type:N',
				column='Forwarder:N',
				tooltip='TEU:Q',
				text='TEU:Q'
			)
		
			
			bar_y = alt.Chart(finalselection, height=500, width={"step": 120}).mark_bar().encode(
				x='Type:O',
				y= alt.Y(('%Filled:Q'), axis=alt.Axis(format='%')),
				color='%Type:N',
				column='Forwarder:N',
				tooltip='TEU:Q',
				text='%Filled:Q'
			)

			left_column, right_column = st.columns(2)
			with left_column:
				st.altair_chart(bar_x)

			with right_column:
				st.altair_chart(bar_y)
				
				
			finalselection = finalselection.sort_values(by=['Forwarder','Type'],ascending=True)
			
			total_all_teu = int(just_a_shot['Allocation'].sum())
			used_teu = int(just_a_shot['Pipeline'].sum())
			con_teu = int(just_a_shot['Confirmed'].sum())
			bal_pip_teu = total_all_teu - used_teu
			bal_con_teu = total_all_teu - con_teu


			left_column, mid_lft_column , cntr ,mid_rt_column,right_column = st.columns(5)
			with left_column:
				st.subheader("Allocation:")
				st.subheader(total_all_teu)

			with mid_lft_column:
				st.subheader("Pipeline TEU:")
				st.subheader(used_teu)

			with cntr:
				st.subheader("Balance(pipeline):")
				st.subheader(bal_pip_teu)  

			with mid_rt_column:
				st.subheader("Confirmed TEU:")
				st.subheader(con_teu)  
					
			with right_column:
				st.subheader("Balance(Confirmed):")
				st.subheader(bal_con_teu)

			st.markdown("---")
			st.write(just_a_shot)
		
		else:
				
			df_selection = source.query("Week==@Week & POL==@POL & Forwarder==@Forwarder")

			per_of_total = df_selection.copy()

			per_of_totalII = per_of_total.pivot_table(index=["Year","Month","Week","POL","Forwarder"],
													  columns='Type', values='TEU', aggfunc='sum').reset_index()

			per_of_totalII["%Confirmed"] = per_of_totalII["Confirmed"] / per_of_totalII["Allocation"]
			per_of_totalII["%Pipeline"] = per_of_totalII["Pipeline"] / per_of_totalII["Allocation"]
			per_of_totalII = per_of_totalII.replace([np.inf, -np.inf], 0)
			per_of_totalII = per_of_totalII.rename_axis(None, axis=1)
			per_of_totalII = per_of_totalII.fillna(0)

			just_a_shot = per_of_totalII.copy()
			per_of_totalIIV1 = per_of_totalII.copy()

			per_of_totalIIV1 = per_of_totalIIV1[["Year","Month","Week","POL","Forwarder",
											   "Allocation","Confirmed","Pipeline"]]
											   
			per_of_totalIIV1 = pd.melt(per_of_totalIIV1, id_vars =["Year","Month","Week","POL","Forwarder"],
					value_vars =["Allocation","Confirmed","Pipeline"], var_name='Type', value_name='TEU')

			per_of_totalIIV2 = per_of_totalII.copy()

			per_of_totalIIV2 = per_of_totalIIV2[["Year","Month","Week","POL","Forwarder","%Confirmed","%Pipeline"]] 

			per_of_totalIIV2 = pd.melt(per_of_totalIIV2, id_vars =["Year","Month","Week","POL","Forwarder"],
									   value_vars =["%Confirmed","%Pipeline"], var_name='%Type', value_name='%Filled')

			per_of_totalIIV2["Type"] = np.where(per_of_totalIIV2["%Type"] == "%Confirmed", "Confirmed", "Pipeline")


			finalselection = pd.merge(per_of_totalIIV1, per_of_totalIIV2,
									  on=["Year","Month","Week","POL","Forwarder", "Type"],
									  how="outer")

			finalselection["%Type"] = np.where(finalselection["Type"] == "Allocation",
											   "Total Allocation",
											   finalselection["%Type"])																		

			finalselection["%Filled"] = np.where(finalselection["Type"] == "Allocation",
											   1,
											   finalselection["%Filled"])
											   
			finalselection['%Filled'] = round(finalselection['%Filled'], 2) * 100


			#--- Main Page ---
			st.title(":anchor: Port: "+str(finalselection.loc[0,"POL"]))
			st.subheader(":calendar: Week: "+str(finalselection.loc[0,"Week"]))

			Allocation_TEU = px.bar(
				finalselection,
				x = "TEU",
				y = "Type", 
				orientation="h",
				title="<b>Allocation Vs. Actual",
				color='Type',
				text="TEU"
			)


			per_of_totalIII = px.bar(
				finalselection,
				x = "%Filled",
				y = "%Type", 
				orientation="h",
				title="<b>%Allocation Vs. %Actual",
				color='%Type',
				text=[f'{i}%' for i in finalselection['%Filled']]
			) 

			per_of_totalIII.layout.xaxis.ticksuffix=".0%" 


			left_column, right_column = st.columns(2)
			with left_column:
				st.plotly_chart(Allocation_TEU)

			with right_column:
				st.plotly_chart(per_of_totalIII)
				

			total_all_teu = int(just_a_shot['Allocation'].sum())
			used_teu = int(just_a_shot['Pipeline'].sum())
			con_teu = int(just_a_shot['Confirmed'].sum())
			bal_pip_teu = total_all_teu - used_teu
			bal_con_teu = total_all_teu - con_teu
			
			st.write(just_a_shot)


			left_column, mid_lft_column , cntr ,mid_rt_column,right_column = st.columns(5)
			with left_column:
				st.subheader("Allocation:")
				st.subheader(total_all_teu)

			with mid_lft_column:
				st.subheader("Pipeline TEU:")
				st.subheader(used_teu)

			with cntr:
				st.subheader("Balance(pipeline):")
				st.subheader(bal_pip_teu)  

			with mid_rt_column:
				st.subheader("Confirmed TEU:")
				st.subheader(con_teu)  
					
			with right_column:
				st.subheader("Balance(Confirmed):")
				st.subheader(bal_con_teu)

			st.markdown("---")
			
############################################################################################################################################



CWs = SliderData["Week"].unique().tolist()


st.sidebar.markdown("###")
st.sidebar.markdown("###")
st.sidebar.markdown("###")
st.sidebar.markdown("###")
st.sidebar.markdown("###")
st.sidebar.markdown("###")
st.sidebar.header("Filter by CW:")

weekly_range = st.sidebar.slider("Start & End CW:", min_value=min(CWs), max_value=max(CWs), value=(min(CWs),max(CWs)))


SliderData = SliderData[SliderData["Week"]>= weekly_range[0]]
SliderData = SliderData[SliderData["Week"]<= weekly_range[1]]

#--- Main Page ---
per_of_totalSly = SliderData.copy()


per_of_totalSlyII = per_of_totalSly.pivot_table(index=["Year","Month","Week","POL","Forwarder"],
 columns='Type', values='TEU', aggfunc='sum').reset_index()


per_of_totalSlyII["%Confirmed"] = per_of_totalSlyII["Confirmed"] / per_of_totalSlyII["Allocation"]
per_of_totalSlyII["%Pipeline"] = per_of_totalSlyII["Pipeline"] / per_of_totalSlyII["Allocation"]
per_of_totalSlyII = per_of_totalSlyII.replace([np.inf, -np.inf], 0)
per_of_totalSlyII = per_of_totalSlyII.rename_axis(None, axis=1)
per_of_totalSlyII = per_of_totalSlyII.fillna(0)

just_a_shot = per_of_totalSlyII.copy()
per_of_totalSlyV1 = per_of_totalSlyII.copy()

finalselectionSly = just_a_shot[["Year", "Month", "Week", "POL", "Forwarder", "Allocation", "Confirmed", "Pipeline", "Allo"]]

st.sidebar.subheader("Chart Filter")

polsly = finalselectionSly["POL"].unique()
polsly = polsly.tolist()
polsly.append(DEFAULT)
polsly = sorted(polsly)

fwdsly = finalselectionSly["Forwarder"].unique()
fwdsly = fwdsly.tolist()
fwdsly.append(DEFAULT)
fwdsly = sorted(fwdsly)

polsly = st.sidebar.selectbox("Select POL:", polsly)

fwdsly = st.sidebar.selectbox("Select Forwarder:", fwdsly)


if polsly == DEFAULT and fwdsly == DEFAULT:
	st.title("Allocation Vs. Pipeline Vs. Confirmed")
	st.subheader(":calendar: CW Range: "+str(weekly_range[0])+"-"+str(weekly_range[1]))
	st.subheader("All Ports and Forwarders")
	

	bar = alt.Chart(finalselectionSly).mark_bar().encode(
		x='Week:O',
		y=alt.Y('sum(Allocation)', title='TEU'),
		tooltip='sum(Allocation)',
		color=alt.condition(
        alt.datum.Week == CurrentWeek, 
        alt.value('cadetblue'),     
        alt.value('lightgrey')),
	).properties(width=1600, height=600, title=alt.TitleParams(
        ['YELLOW = Confirmed', 'RED = PIPELINE', 'BARS = FC_Allocation'],
        baseline='bottom',
        orient='bottom',
        anchor='end',
        fontWeight='bold',
        fontSize=12,
		color = 'black')
	)

	line = alt.Chart(finalselectionSly).mark_line(color="yellow").encode(
		x='Week:O',
		y=alt.Y('sum(Confirmed)', title='TEU'),
		size=alt.value(6),
		tooltip='sum(Confirmed)'
	)

	bar = bar + line

	line2 = alt.Chart(finalselectionSly).mark_line(color="red").encode(
		x='Week:O',
		y=alt.Y('sum(Pipeline)', title='TEU'),
		size=alt.value(6),
		tooltip='sum(Pipeline)'
	)

	bar = bar + line2
	
	text = alt.Chart(finalselectionSly).mark_text(color='black',dy=-5,dx=0).encode(
    x='Week:O',
    y=alt.Y('sum(Allocation)', title='TEU'),
    detail='sum(Allocation)',
    text=alt.Text('sum(Allocation)')
)
	bar = bar + text
	
	text2 = alt.Chart(finalselectionSly).mark_text(color='red',dy=-15,dx=-10).encode(
    x='Week:O',
    y=alt.Y('sum(Pipeline)', title='TEU'),
    detail='sum(Pipeline)',
    text=alt.Text('sum(Pipeline)')
)
	bar = bar + text2

	st.altair_chart(bar)
	
	st.markdown("---")

	Total_Allocation = int(finalselectionSly['Allocation'].sum())
	pipeline_teu = int(finalselectionSly['Pipeline'].sum())
	con_teu = int(finalselectionSly['Confirmed'].sum())
	bal_pip_teu = Total_Allocation - pipeline_teu
	bal_con_teu = Total_Allocation - con_teu


	left_column, mid_lft_column , cntr ,mid_rt_column,right_column = st.columns(5)
	with left_column:
		st.subheader("Total Allocation:")
		st.subheader(Total_Allocation)

	with mid_lft_column:
		st.subheader("Pipeline TEU:")
		st.subheader(pipeline_teu)

	with cntr:
		st.subheader("Balance(pipeline):")
		st.subheader(bal_pip_teu)  

	with mid_rt_column:
		st.subheader("Confirmed TEU:")
		st.subheader(con_teu )  
			
	with right_column:
		st.subheader("Balance(Confirmed):")
		st.subheader(bal_con_teu)

	st.markdown("---")
	
	st.write(finalselectionSly)
	
elif polsly == DEFAULT and fwdsly != DEFAULT:
	finalselectionSly = finalselectionSly.query("Forwarder==@fwdsly")
	finalselectionSly.reset_index(drop=True,inplace=True)
	
	st.title("Allocation Vs. Pipeline Vs. Confirmed")
	st.subheader(":calendar: CW Range: "+str(weekly_range[0])+"-"+str(weekly_range[1]))
	st.subheader("All Ports & "+str(finalselectionSly.loc[0,"Forwarder"]))
	

	bar = alt.Chart(finalselectionSly).mark_bar().encode(
		x='Week:O',
		y=alt.Y('sum(Allocation)', title='TEU'),
		color=alt.condition(
        alt.datum.Week == CurrentWeek, 
        alt.value('cadetblue'),     
        alt.value('lightgrey') 
     )
	).properties(width=1600, height=600, title=alt.TitleParams(
        ['YELLOW = Confirmed', 'RED = PIPELINE', 'BLUE = ALLO', 'BARS = FC_Allocation'],
        baseline='bottom',
        orient='bottom',
        anchor='end',
        fontWeight='bold',
        fontSize=12,
		color = 'black')
	)

	line = alt.Chart(finalselectionSly).mark_line(color="yellow").encode(
		x='Week:O',
		y=alt.Y('sum(Confirmed)', title='TEU'),
		size=alt.value(6)
	)

	bar = bar + line

	line2 = alt.Chart(finalselectionSly).mark_line(color="red").encode(
		x='Week:O',
		y=alt.Y('sum(Pipeline)', title='TEU'),
		size=alt.value(6)
	)

	bar = bar + line2
 	
	line3 = alt.Chart(finalselectionSly).mark_line(color="blue").encode(
		x='Week:O',
		y=alt.Y('min(Allo)', title='TEU'),
		size=alt.value(6)
	)

	bar = bar + line3   


	
	text = alt.Chart(finalselectionSly).mark_text(color='black',dy=-5,dx=0).encode(
    x='Week:O',
    y=alt.Y('sum(Allocation)', title='TEU'),
    detail='sum(Allocation)',
    text=alt.Text('sum(Allocation)')
)
	bar = bar + text
	
	text2 = alt.Chart(finalselectionSly).mark_text(color='red',dy=-12,dx=-10).encode(
    x='Week:O',
    y=alt.Y('sum(Pipeline)', title='TEU'),
    detail='sum(Pipeline)',
    text=alt.Text('sum(Pipeline)')
)
	bar = bar + text2

	
	st.altair_chart(bar)
	

	st.markdown("---")

	Total_Allocation = int(finalselectionSly['Allocation'].sum())
	pipeline_teu = int(finalselectionSly['Pipeline'].sum())
	con_teu = int(finalselectionSly['Confirmed'].sum())
	bal_pip_teu = Total_Allocation - pipeline_teu
	bal_con_teu = Total_Allocation - con_teu


	left_column, mid_lft_column , cntr ,mid_rt_column,right_column = st.columns(5)
	with left_column:
		st.subheader("Total Allocation:")
		st.subheader(Total_Allocation)

	with mid_lft_column:
		st.subheader("Pipeline TEU:")
		st.subheader(pipeline_teu)

	with cntr:
		st.subheader("Balance(pipeline):")
		st.subheader(bal_pip_teu)  

	with mid_rt_column:
		st.subheader("Confirmed TEU:")
		st.subheader(con_teu )  
			
	with right_column:
		st.subheader("Balance(Confirmed):")
		st.subheader(bal_con_teu)

	st.markdown("---")
	
	st.write(finalselectionSly)

elif polsly != DEFAULT and fwdsly == DEFAULT:
	finalselectionSly = finalselectionSly.query("POL==@polsly")
	finalselectionSly.reset_index(drop=True,inplace=True)
	
	st.title(":anchor: Port: "+str(finalselectionSly.loc[0,"POL"]))
	st.title("Allocation Vs. Pipeline Vs. Confirmed")
	st.subheader(":calendar: CW Range: "+str(weekly_range[0])+"-"+str(weekly_range[1]))
	st.subheader("All Forwarders")

	
	bar = alt.Chart(finalselectionSly).mark_bar().encode(
		x='Week:O',
		y=alt.Y('sum(Allocation)', title='TEU'),
		color=alt.condition(
        alt.datum.Week == CurrentWeek, 
        alt.value('cadetblue'),     
        alt.value('lightgrey') 
     )
	).properties(width=1600, height=600, title=alt.TitleParams(
        ['YELLOW = Confirmed', 'RED = PIPELINE', 'BARS = FC_Allocation'],
        baseline='bottom',
        orient='bottom',
        anchor='end',
        fontWeight='bold',
        fontSize=12,
		color = 'black')
	)

	line = alt.Chart(finalselectionSly).mark_line(color="yellow").encode(
		x='Week:O',
		y=alt.Y('sum(Confirmed)', title='TEU'),
		size=alt.value(6)
		
	)

	bar = bar + line

	line2 = alt.Chart(finalselectionSly).mark_line(color="red").encode(
		x='Week:O',
		y=alt.Y('sum(Pipeline)', title='TEU'),
		size=alt.value(6)
	)

	bar = bar + line2


	text = alt.Chart(finalselectionSly).mark_text(color='black',dy=-5,dx=0).encode(
    x='Week:O',
    y=alt.Y('sum(Allocation)', title='TEU'),
    detail='sum(Allocation)',
    text=alt.Text('sum(Allocation)')
)
	bar = bar + text
	
	text2 = alt.Chart(finalselectionSly).mark_text(color='red',dy=-12,dx=-10).encode(
    x='Week:O',
    y=alt.Y('sum(Pipeline)', title='TEU'),
    detail='sum(Pipeline)',
    text=alt.Text('sum(Pipeline)')
)
	bar = bar + text2

	
	st.altair_chart(bar)
	

	st.markdown("---")

	Total_Allocation = int(finalselectionSly['Allocation'].sum())
	pipeline_teu = int(finalselectionSly['Pipeline'].sum())
	con_teu = int(finalselectionSly['Confirmed'].sum())
	bal_pip_teu = Total_Allocation - pipeline_teu
	bal_con_teu = Total_Allocation - con_teu


	left_column, mid_lft_column , cntr ,mid_rt_column,right_column = st.columns(5)
	with left_column:
		st.subheader("Total Allocation:")
		st.subheader(Total_Allocation)

	with mid_lft_column:
		st.subheader("Pipeline TEU:")
		st.subheader(pipeline_teu)

	with cntr:
		st.subheader("Balance(pipeline):")
		st.subheader(bal_pip_teu)  

	with mid_rt_column:
		st.subheader("Confirmed TEU:")
		st.subheader(con_teu )  
			
	with right_column:
		st.subheader("Balance(Confirmed):")
		st.subheader(bal_con_teu)

	st.markdown("---")
	
	st.write(finalselectionSly)
else: 			
	finalselectionSly = finalselectionSly.query("POL==@polsly & Forwarder==@fwdsly")
	finalselectionSly.reset_index(drop=True,inplace=True)
	
	st.title(":anchor: "+str(finalselectionSly.loc[0,"POL"])+"-"+str(finalselectionSly.loc[0,"Forwarder"]))
	st.title("Allocation Vs. Pipeline Vs. Confirmed")
	st.subheader(":calendar: CW Range: "+str(weekly_range[0])+"-"+str(weekly_range[1]))


	bar = alt.Chart(finalselectionSly).mark_bar().encode(
		x='Week:O',
		y=alt.Y('sum(Allocation)', title='TEU'),
		color=alt.condition(
        alt.datum.Week == CurrentWeek, 
        alt.value('cadetblue'),     
        alt.value('lightgrey') 
     )
	).properties(width=1600, height=600, title=alt.TitleParams(
        ['YELLOW = Confirmed', 'RED = PIPELINE', 'BARS = FC_Allocation'],
        baseline='bottom',
        orient='bottom',
        anchor='end',
        fontWeight='bold',
        fontSize=12,
		color = 'black')
	)

	line = alt.Chart(finalselectionSly).mark_line(color="yellow").encode(
		x='Week:O',
		y=alt.Y('sum(Confirmed)', title='TEU'),
		size=alt.value(6)
	)

	bar = bar + line

	line2 = alt.Chart(finalselectionSly).mark_line(color="red").encode(
		x='Week:O',
		y=alt.Y('sum(Pipeline)', title='TEU'),
		size=alt.value(6)
	)

	bar = bar + line2

	text = alt.Chart(finalselectionSly).mark_text(color='black',dy=-5,dx=0).encode(
    x='Week:O',
    y=alt.Y('sum(Allocation)', title='TEU'),
    detail='sum(Allocation)',
    text=alt.Text('sum(Allocation)')
)
	bar = bar + text
	
	text2 = alt.Chart(finalselectionSly).mark_text(color='red',dy=-12,dx=-10).encode(
    x='Week:O',
    y=alt.Y('sum(Pipeline)', title='TEU'),
    detail='sum(Pipeline)',
    text=alt.Text('sum(Pipeline)')
)
	bar = bar + text2

	
	st.altair_chart(bar)

	st.markdown("---")

	Total_Allocation = int(finalselectionSly['Allocation'].sum())
	pipeline_teu = int(finalselectionSly['Pipeline'].sum())
	con_teu = int(finalselectionSly['Confirmed'].sum())
	bal_pip_teu = Total_Allocation - pipeline_teu
	bal_con_teu = Total_Allocation - con_teu


	left_column, mid_lft_column , cntr ,mid_rt_column,right_column = st.columns(5)
	with left_column:
		st.subheader("Total Allocation:")
		st.subheader(Total_Allocation)

	with mid_lft_column:
		st.subheader("Pipeline TEU:")
		st.subheader(pipeline_teu)

	with cntr:
		st.subheader("Balance(pipeline):")
		st.subheader(bal_pip_teu)  

	with mid_rt_column:
		st.subheader("Confirmed TEU:")
		st.subheader(con_teu )  
			
	with right_column:
		st.subheader("Balance(Confirmed):")
		st.subheader(bal_con_teu)

	st.markdown("---")
	
	st.write(finalselectionSly)
