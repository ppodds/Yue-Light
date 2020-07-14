### **開發環境:**  

Python 3.7.5 x64  

ffmpeg 20200417  

### **額外擴充(需用pip install安裝):**  

discord.py  

PyNaCl  

youtube-dl  

### **資料夾內容:**  

Bot: 內含程式碼及部分資料  

Bot\api: 內含程式庫程式碼  

Bot\cogs: cogs的程式碼，指令和事件都集中於此(事件和指令要明確分開，單一事件或同類指令分開編寫)  

已知常見問題: 監聽on_message會讓同模組的指令失效是正常現象，官方文檔有說明)  

Bot\data: 儲存資料  

Bot\data\statusList: 存放Bot顯示的狀態訊息，會定時切換，可以在程式碼中修改時間  

downloads: 點歌下載的檔案集中於此，若刪除下次點歌就要再次下載  

music: 本地撥放的音樂檔案，可自行投入  