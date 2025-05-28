import streamlit as st
import requests
import pandas as pd

API_BASE = "https://web-apps.orangetree-cce831db.eastus2.azurecontainerapps.io"

st.set_page_config(page_title="MLB 球員資料查詢", layout="wide")
st.title("⚾ MLB 球員成績總覽")

st.markdown("### 資料來源：Azure SQL Database")

# 取得所有資料
@st.cache_data(ttl=300)
def fetch_all_players():
    res = requests.get(f"{API_BASE}/players_full")
    if res.status_code == 200:
        return pd.DataFrame(res.json())
    else:
        st.error("❌ 無法取得資料")
        return pd.DataFrame()

# 載入資料
df = fetch_all_players()

if df.empty:
    st.stop()

# 清理數值欄位型別
for col in ['homeRuns', 'avg', 'ops']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 側邊選單：篩選條件
year = st.sidebar.selectbox("選擇年度", sorted(df['year'].unique(), reverse=True))
team = st.sidebar.selectbox("選擇球隊", ["全部"] + sorted(df['team'].dropna().unique()))
sort_by = st.sidebar.selectbox("排序欄位", ["homeRuns", "avg", "ops"])
sort_order = st.sidebar.radio("排序方式", ["由高至低", "由低至高"])

# 過濾
df_filtered = df[df['year'] == year]
if team != "全部":
    df_filtered = df_filtered[df_filtered['team'] == team]

# 排序
df_sorted = df_filtered.sort_values(by=sort_by, ascending=(sort_order == "由低至高"))

# 顯示表格
st.dataframe(
    df_sorted[[
        'playerFullName', 'team', 'year', 'homeRuns', 'avg', 'ops', 'plateAppearances',
        'hits', 'doubles', 'triples', 'strikeOuts', 'baseOnBalls'
    ]].reset_index(drop=True),
    use_container_width=True
)
