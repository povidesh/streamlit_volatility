import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import base64
from scipy.stats.mstats import winsorize
from datetime import date as dt
from datetime import timedelta

site_link = "https://www.fairvalue.co.il"
upper_logo_url = "logo.jpg"
bottom_logo_url = "fv2.jpg"

with open(upper_logo_url, "rb") as f:
    img_bytes = f.read()
    encoded = base64.b64encode(img_bytes).decode()

# Inject as HTML <img>
st.markdown(
    f"""
    <a href="{site_link}" target="_blank">
	    <img src="data:image/jpeg;base64,{encoded}" width="200">
    </a>
    """,
    unsafe_allow_html=True
)

with open(bottom_logo_url, "rb") as f:
    img_bytes = f.read()
    encoded_bottom = base64.b64encode(img_bytes).decode()
st.markdown(
    f"""
    <style>
    .bottom-right-logo {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 100;
    }}
    </style>

    <div class="bottom-right-logo">
        <img src="data:image/jpeg;base64,{encoded_bottom}" width="200">
    </div>
    """,
    unsafe_allow_html=True
)


st.write("""
	### Do you want to check volatility of some stock?""")

st.write("""
	#### Please input ticker""")
ric = st.text_input("Ticker")

current_date = dt.today()

st.write("""
	#### Please input effective date""")
col1, col2, col3 = st.columns(3)

with col1:
	y=st.number_input("Year",value=current_date.year)
with col2:
	m=st.number_input("Month",value=current_date.month)
with col3:
	d=st.number_input("Day",value=current_date.day)

calc_date=dt(y,m,d)

st.write("""
	#### Please input lookback period in years""")
dif = st.number_input("Ttm", min_value=0.1, max_value=10.0, value=3.0, step=0.1)
sdate=calc_date-timedelta(days=dif*365)

if st.button("Calculate"):
	if ric and sdate:

		df = yf.download(ric, start=str(sdate), end=str(calc_date+ timedelta(days=1)),auto_adjust=False)
		df.columns = df.columns.droplevel(1)
		df = df.sort_values(by='Date',ascending=False)
		df.index = pd.to_datetime(df.index).tz_localize(None)

		#Volatility part start
		df['log_returns']=np.log(df['Adj Close']/df['Adj Close'].shift(-1))
		df["winsorized_returns_2"] = winsorize(df['log_returns'], limits=[0.01, 0.01])
		df["winsorized_returns_5"] = winsorize(df['log_returns'], limits=[0.025, 0.025])
		df["winsorized_returns_10"] = winsorize(df['log_returns'], limits=[0.05, 0.05])

		volatility = df['log_returns'].std()*252**.5
		volatilityW2 = df["winsorized_returns_2"].std()*252**.5
		volatilityW5 = df["winsorized_returns_5"].std()*252**.5
		volatilityW10 = df["winsorized_returns_10"].std()*252**.5

		st.write("""
			#### Volatility summary""")
		st.write("Daily Volatility: "+"{:.1%}".format(volatility))
		st.write("Winsorized 2%: "+"{:.1%}".format(volatilityW2))   
		st.write("Winsorized 5%: "+"{:.1%}".format(volatilityW5)) 
		st.write("Winsorized 10%: "+"{:.1%}".format(volatilityW10))
		st.write("Price chart of "+ric)
		st.line_chart(df['Adj Close'])




