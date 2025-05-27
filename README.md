# Azure_期末專案

1. pip install -r requirements.txt

(在azure建立資料庫後執行db_writer.py)

2. 在終端機執行 python app.py

3. 執行 streamlit run mlb_streamlit_app.py


#Docker 
docker build -t mlb-app .

docker run -d -p 8000:8000 --env-file .env mlb-app

http://localhost:8000/players_full
