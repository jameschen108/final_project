FROM python:3.12-slim

# 安裝系統相依套件與 ODBC 所需函式庫
RUN apt-get update && apt-get install -y \
    curl gnupg2 unixodbc unixodbc-dev libgssapi-krb5-2 \
    apt-transport-https ca-certificates gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# 匯入 Microsoft GPG 金鑰
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

# 新增 Microsoft ODBC 套件來源
RUN echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list

# 安裝 Microsoft ODBC Driver 18
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# 建立應用目錄
WORKDIR /app

# 複製需求與安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 開放 Flask 預設 Port（方便 Azure 使用）
EXPOSE 8000

# 啟動 Flask 應用（建議顯式指定 host/port）
CMD ["python", "app.py"]
