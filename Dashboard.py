import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

# ============================================
# FETCH REAL LIVE DATA 🔥
# ============================================


@st.cache_data(ttl=300)  # refresh every 5 minutes!
def get_stock_data():
    symbols = {
        "Apple":     "AAPL",
        "Google":    "GOOGL",
        "Microsoft": "MSFT",
        "Tesla":     "TSLA",
        "Amazon":    "AMZN"
    }
    
    data = []
    for company, symbol in symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            info = ticker.info
            
            current_price = round(hist["Close"].iloc[-1], 2)
            prev_price = round(hist["Close"].iloc[-2], 2)
            change = round(((current_price - prev_price) / prev_price) * 100, 2)
            volume = int(hist["Volume"].iloc[-1])
            market_cap = round(info.get("marketCap", 0) / 1e9, 1)
            
            data.append({
                "Company": company,
                "Symbol": symbol,
                "Price": current_price,
                "Change": change,
                "Volume": volume,
                "MarketCap": market_cap
            })
        except:
            pass
    
    return pd.DataFrame(data)

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# ============================================
# LOAD DATA
# ============================================
with st.spinner("Fetching live market data... 📡"):
    df = get_stock_data()

# ============================================
# SIDEBAR
# ============================================
st.sidebar.title("📊 Controls")
selected_company = st.sidebar.selectbox("Select Company", df["Company"])
show_volume = st.sidebar.checkbox("Show Volume Data")
chart_type = st.sidebar.radio("Chart Type", ["Bar", "Line"])
st.sidebar.caption("Recommended Chart: BAR")
st.sidebar.divider()
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# ============================================
# MAIN PAGE
# ============================================
st.title("📈 Stock Market Dashboard")
st.caption("🔴 Live Market Data — Updates every 5 minutes")

filtered = df[df["Company"] == selected_company].iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Company", filtered["Symbol"])
col2.metric("Price", f"${filtered['Price']}")
col3.metric("Change", f"{filtered['Change']}%")
col4.metric("Market Cap", f"${filtered['MarketCap']}B")

st.divider()

if filtered["Change"] > 0:
    st.success(f"▲ +{filtered['Change']}% Today")
else:
    st.error(f"▼ {filtered['Change']}% Today")

# ============================================
# TABS
# ============================================
tab1, tab2, tab3, tab4 = st.tabs(["📈 Price Chart", "🥧 Market Cap", "📋 Data", "⚡ Compare"])

with tab1:
    if chart_type == "Bar":
        fig = px.bar(df, x="Company", y="Price",
                     color="Company",
                     title="Live Stock Prices 🔴")
    else:
        fig = px.line(df, x="Company", y="Price",
                      markers=True,
                      title="Stock Price Trend 🔴")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = px.pie(df, values="MarketCap", names="Company",
                  title="Market Cap Distribution")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("📊 Live Market Data")
    st.dataframe(df, use_container_width=True)

    if show_volume:
        st.subheader("📊 Trading Volume")
        fig_vol = px.bar(df, x="Company", y="Volume",
                        color="Company",
                        title="Trading Volume")
        st.plotly_chart(fig_vol, use_container_width=True)

    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Live Data as CSV",
        data=csv_data,
        file_name="live_market_data.csv",
        mime="text/csv"
    )

with tab4:
    st.subheader("⚡ Compare Two Companies")

    col_a, col_b = st.columns(2)

    with col_a:
        company_a = st.selectbox(
            "Select Company A", 
            df["Company"], 
            key="company_a"
            )

    with col_b:
        company_b = st.selectbox(
            "Select Company B", 
            df["Company"],
            index=1,
            key="company_b"
            )

    data_a = df[df["Company"] == company_a].iloc[0]
    data_b = df[df["Company"] == company_b].iloc[0]

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("","")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(f"🔵 {company_a}")
        st.metric("Price", f"${data_a['Price']}")
        st.metric("Change", f"{data_a['Change']}%")
        st.metric("Market Cap", f"${data_a['MarketCap']}B")
        st.metric("Volume", f"{data_a['Volume']:,}")
        
        if data_a['Change'] > 0:
            st.success(f"▲ +{data_a['Change']}%")
        else:
            st.error(f"▼ {data_a['Change']}%")


    with col_right:
        st.subheader(f"🔴 {company_b}")
        st.metric("Price", f"${data_b['Price']}")
        st.metric("Change", f"{data_b['Change']}%")
        st.metric("Market Cap", f"${data_b['MarketCap']}B")
        st.metric("Volume", f"{data_b['Volume']:,}")
        
        if data_a['Change'] > 0:
            st.success(f"▲ +{data_b['Change']}%")
        else:
            st.error(f"▼ {data_b['Change']}%")


    st.divider()

    compare_df = pd.DataFrame({
        "Company": [company_a, company_b],
        "Price": [data_a['Price'], data_b['Price']],
        "Change": [data_a['Change'],data_b['Change']],
        "MarketCap": [data_a['MarketCap'], data_b['MarketCap']],
    })

    metric_choice = st.radio(
        "Compare by:",
        ["Price", "MarketCap", "Change"],
        horizontal=True
    )
    
    fig_compare = px.bar(
        compare_df,
        x="Company",
        y=metric_choice,
        color="Company",
        title=f"{company_a} vs {company_b} — {metric_choice}",
        color_discrete_sequence=["#636EFA", "#EF553B"]
    )
    st.plotly_chart(fig_compare, use_container_width=True)


