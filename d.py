#from turtle import width
#import seaborn
#from re import template
#from matplotlib import use
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import warnings
import plotly.figure_factory as ff
warnings.filterwarnings('ignore')

st.set_page_config(page_title='SuperStore!',page_icon=":bar_chart:",layout="wide")
# icons :  https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
st.title(" :bar_chart: Sample SuperStore EDA")
st.markdown("<style>div.block-container{padding-top:lrem;}</style>",unsafe_allow_html=True)

f1 =st.file_uploader(':file_folder: Upload a file',type=(['csv','txt','xlsx','xls']))
if f1 is not None:
    filename = f1.name
    st.write(filename)
    df = pd.read_csv(filename,encoding='ISO-8859-1')
else:
    os.chdir(r"C:\Users\Vishal\OneDrive\Desktop\streamlit")
    df = pd.read_csv('Sample - Superstore.csv',encoding='ISO-8859-1')

col1 , col2=  st.columns((2))
df['Order Date'] = pd.to_datetime(df['Order Date'])

#getting min,max data
startDate = pd.to_datetime(df['Order Date']).min()
endDate = pd.to_datetime(df['Order Date']).max()

with col1:
    date1 = pd.to_datetime(st.date_input('Start Date',startDate))
with col2:
    date2 = pd.to_datetime(st.date_input('End Date',endDate))

df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()
#selecting a region
region = st.sidebar.multiselect("Pick your Region",df['Region'].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)]

#selecting a state
state = st.sidebar.multiselect('Select the State',df2['State'].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2['State'].isin(state)]

#select a city
city = st.sidebar.multiselect('Select the City',df3['City'].unique())

#filter the data base on region , state, city
if not region and not state and not city:
    filtere_df = df
elif not state and not city:
    filtere_df = df[df['Region'].isin(region)]
elif not region and not city:
    filtere_df = df[df['State'].isin(state)]
elif state and city:
    filtere_df = df3[df['State'].isin(state) &df3['City'].isin(city)]
elif region and city:
    filtere_df = df3[df['Region'].isin(region) &df3['City'].isin(city)]
elif region and state:
    filtere_df = df3[df['Region'].isin(region) &df3['State'].isin(state)]
elif city:
    filtere_df = df3[df3['City'].isin(city)]
else:
    filtere_df = df3[df3['Region'].isin(region) & df3['State'].isin(state) & df3['City'].isin(city)]

category_df = filtere_df.groupby(by = ['Category'],as_index = False)['Sales'].sum()

with col1:
    st.subheader('Category wise sales')
    fig = px.bar(category_df,x = 'Category',y = 'Sales',text = ['${:,.2f}'.format(x) for x in category_df['Sales']],
                 template='seaborn')
    st.plotly_chart(fig,use_container_width=True,height = 200)

with col2:
    st.subheader('Region wise Sales')
    fig = px.pie(filtere_df,values='Sales',names='Region',hole = 0.5)
    fig.update_traces(text= filtere_df['Region'],textposition = 'outside')
    st.plotly_chart(fig,use_container_width=True)

cl1,cl2 = st.columns(2)
with cl1:
    with st.expander('Category_ViewData'):
        st.write(category_df.style.background_gradient(cmap = 'Blues'))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button('Download Data',data = csv,file_name='Category.csv',
                           mime = 'text/csv',help = 'Click here to download data as CSV file')

with cl2:
    with st.expander('Region_ViewData'):
        region = filtere_df.groupby(by = 'Region',as_index = False)['Sales'].sum()
        st.write(region.style.background_gradient(cmap = 'Oranges'))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button('Download Data',data = csv,file_name='Region.csv',
                           mime = 'text/csv',help = 'Click here to download data as CSV file')
        
filtere_df['month_year'] = filtere_df['Order Date'].dt.to_period('M')
st.subheader('Time Series Analysis')
                                             #dt.strftime
linechart = pd.DataFrame(filtere_df.groupby(filtere_df['month_year'].dt.strftime('%Y : %b'))['Sales'].sum()).reset_index()
fig2 = px.line(linechart,x = 'month_year',y = 'Sales',labels={'Sales':'Amount'},height=500,width=1000,template='gridon')
st.plotly_chart(fig2,use_container_width=True)

with st.expander('View Data of Time Series:'):
    st.write(linechart.T.style.background_gradient(cmap = 'Blues'))
    csv = linechart.to_csv(index = False).encode('utf-8')
    st.download_button('Download Data',data = csv,file_name='TimeSeries.csv',mime='text/csv')

#create a tream base on region and category , sub category
st.subheader('Hierarchical view of Sales using TreeMap')
fig3 = px.treemap(filtere_df,path = ['Region','Category','Sub-Category'],values = 'Sales',hover_data = ['Sales'],
                  color = 'Sub-Category')
fig3.update_layout(width = 800,height = 650)
st.plotly_chart(fig3,use_container_width=True)

chart1 , chart2 = st.columns(2)
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtere_df,values = 'Sales',names = 'Segment',template = 'plotly_dark')
    fig.update_traces(text = filtere_df['Segment'],textposition = 'inside')  #outside
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader("Category wise Sales")
    fig = px.pie(filtere_df,values='Sales',names= 'Category',template='xgridoff')#xgridoff
    fig.update_traces(text = filtere_df['Category'],textposition = 'inside')
    st.plotly_chart(fig,use_container_width=True)

st.subheader(':point_right: Month wise Sub-Categoory Sales Summary')
with st.expander('Summary_Table'):
    df_sample = df[0:5][['Region','State','City','Category','Sales','Profit','Quantity','Segment']]
    fig = ff.create_table(df_sample,colorscale='Cividis')
    st.plotly_chart(fig,use_container_width=True)

    st.markdown('Month wise sub-categry table')
    filtere_df['month'] = filtere_df['Order Date'].dt.month_name()
    sub_category_year = pd.pivot_table(data = filtere_df,values = 'Sales',index = ['Sub-Category'],columns='month')
    st.write(sub_category_year.style.background_gradient(cmap = 'Blues'))

#creat a scatter plot
data1 =px.scatter(filtere_df,x = 'Sales',y = 'Profit',size ='Quantity')
data1['layout'].update(title=  'Relationship between Sales & Profit using Scater plot',
                       titlefont = dict(size = 20),xaxis = dict(title = 'Sales',titlefont=  dict(size = 20)),
                                        yaxis = dict(title = 'Profit',titlefont = dict(size = 20)))
st.plotly_chart(data1,use_container_width=True)

with st.expander('View Data'):
    st.write(filtere_df.iloc[:500,1:20:2].style.background_gradient(cmap = 'Oranges'))

#download original dataset
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data',data = csv,file_name='Data.csv',mime = 'text/csv')