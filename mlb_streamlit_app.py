import streamlit as st
import requests
import pandas as pd

API_BASE = "https://web-apps.orangetree-cce831db.eastus2.azurecontainerapps.io"

st.set_page_config(page_title="MLB 球員資料查詢", layout="wide")
st.title("⚾ MLB 球員成績總覽")
st.markdown("### 資料來源：Azure SQL Database")

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

# 數值欄位轉換
for col in ['homeRuns', 'avg', 'ops']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 🔍 球員搜尋功能
st.sidebar.markdown("---")
player_name = st.sidebar.text_input("🔎 搜尋球員姓名", "")

if player_name:
    player_df = df[df['playerFullName'] == player_name]
    if player_df.empty:
        st.warning("找不到該球員。請確認名字是否正確。")
    else:
        # 把 year 移到最前面
        if 'year' in player_df.columns:
            cols = player_df.columns.tolist()
            cols.insert(0, cols.pop(cols.index('year')))
            player_df = player_df[cols]

        st.subheader(f"📊 {player_name} 詳細資料")
        st.dataframe(player_df.reset_index(drop=True), use_container_width=True)

# 🎯 篩選與排序功能
year = st.sidebar.selectbox("選擇年度", sorted(df['year'].unique(), reverse=True))
team = st.sidebar.selectbox("選擇球隊", ["全部"] + sorted(df['team'].dropna().unique()))
sort_by = st.sidebar.selectbox("排序欄位", ["homeRuns", "avg", "ops"])
sort_order = st.sidebar.radio("排序方式", ["由高至低", "由低至高"])

df_filtered = df[df['year'] == year]
if team != "全部":
    df_filtered = df_filtered[df_filtered['team'] == team]

df_sorted = df_filtered.sort_values(by=sort_by, ascending=(sort_order == "由低至高"))

st.dataframe(
    df_sorted[[
        'playerFullName', 'team', 'year', 'homeRuns', 'avg', 'ops', 'plateAppearances',
        'hits', 'doubles', 'triples', 'strikeOuts', 'baseOnBalls'
    ]].reset_index(drop=True),
    use_container_width=True
)