FROM python:3.12-slim

# 安裝系統相依套件
RUN apt-get update && apt-get install -y \
    curl gnupg2 unixodbc-dev gcc g++ apt-transport-https ca-certificates

# 匯入 Microsoft GPG 金鑰
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg

# 新增 Microsoft 套件來源（包含 signed-by）
RUN echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list

# 啟用 Microsoft 套件來源，並安裝 ODBC Driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# 建立應用目錄
WORKDIR /app

# 複製需求與安裝 Python 套件
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY . .

# 預設執行 Flask 應用（你也可以改為 streamlit）
CMD ["python", "app.py"]
