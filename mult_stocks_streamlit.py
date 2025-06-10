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

# st.image(upper_logo_url, width=200)  # Adjust width as needed
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
	### Do you want to check volatility of some stocks?""")

st.write("""
	#### Please input tickers (comma-separated, e.g. AAPL, MSFT, GOOG)""")

ric_input = st.text_input("Tickers")
tickers = [r.strip().upper() for r in ric_input.split(",") if r.strip()]

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
	if tickers and sdate:
		vol_list=[]
		close_df=pd.DataFrame()
		for ric in tickers:

			df = yf.download(ric, start=str(sdate), end=str(calc_date+ timedelta(days=1)),auto_adjust=False)
			df.columns = df.columns.droplevel(1)
			df = df.sort_values(by='Date',ascending=False)
			df.index = pd.to_datetime(df.index).tz_localize(None)
			close_df[ric]=df['Adj Close']

			#Volatility part start
			df['log_returns']=np.log(df['Adj Close']/df['Adj Close'].shift(-1))
			df["winsorized_returns_2"] = winsorize(df['log_returns'], limits=[0.01, 0.01])
			df["winsorized_returns_5"] = winsorize(df['log_returns'], limits=[0.025, 0.025])
			df["winsorized_returns_10"] = winsorize(df['log_returns'], limits=[0.05, 0.05])

			volatility = df['log_returns'].std()*252**.5
			volatilityW2 = df["winsorized_returns_2"].std()*252**.5
			volatilityW5 = df["winsorized_returns_5"].std()*252**.5
			volatilityW10 = df["winsorized_returns_10"].std()*252**.5
			vol_list.append([ric,volatility,volatilityW2,volatilityW5,volatilityW10])

		
		if len(tickers)>1:
			columns = ["Ticker", "Volatility", "Winsorized 2%", "Winsorized 5%", "Winsorized 10%"]
			df_summary = pd.DataFrame(vol_list, columns=columns)
			summary_row = pd.DataFrame({
			    "Ticker": ["Mean", "Median"],
			    "Volatility": [df_summary["Volatility"].mean(), df_summary["Volatility"].median()],
			    "Winsorized 2%": [df_summary["Winsorized 2%"].mean(), df_summary["Winsorized 2%"].median()],
			    "Winsorized 5%": [df_summary["Winsorized 5%"].mean(), df_summary["Winsorized 5%"].median()],
			    "Winsorized 10%": [df_summary["Winsorized 10%"].mean(), df_summary["Winsorized 10%"].median()]
			})
			df_summary = pd.concat([df_summary, summary_row], ignore_index=True)


			df_summary_formatted = df_summary.copy()
			for col in ["Volatility", "Winsorized 2%", "Winsorized 5%", "Winsorized 10%"]:
			    df_summary_formatted[col] = df_summary_formatted[col].apply(lambda x: "{:.1%}".format(x))

			st.write("""
				#### Volatility summary""")
			def style_last_two_rows(row):
			    last_two_indices = df_summary_formatted.iloc[-2:].index
			    if row.name in last_two_indices:
			        return ['text-align: center; font-style: italic; font-weight: bold'] * len(row)
			    else:
			        return ['text-align: center'] * len(row)

			styled_df = df_summary_formatted.style.apply(style_last_two_rows, axis=1).hide(axis="index")
			styled_html = styled_df.to_html()
			st.markdown(styled_html, unsafe_allow_html=True)

			st.write("Relative price chart of stocks")
			close_df_relative = close_df / close_df.iloc[-1] * 100

			st.line_chart(close_df_relative)
			st.write("Price chart of stocks")
		else:
			st.write("""
			#### Volatility summary""")
			st.write("Daily Volatility: "+"{:.1%}".format(volatility))
			st.write("Winsorized 2%: "+"{:.1%}".format(volatilityW2))   
			st.write("Winsorized 5%: "+"{:.1%}".format(volatilityW5)) 
			st.write("Winsorized 10%: "+"{:.1%}".format(volatilityW10))
			st.write("Price chart of stock")
		
		st.line_chart(close_df)




