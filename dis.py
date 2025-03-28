import requests
from datetime import datetime
import pytz

def get_earthquake_data():
    # ใช้ USGS API เพื่อดึงข้อมูลแผ่นดินไหวล่าสุด
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",  # ข้อมูลในรูปแบบ GeoJSON
        "limit": 1,  # ดึงข้อมูลแค่เหตุการณ์ล่าสุด
        "orderby": "time",  # เรียงลำดับจากใหม่ไปเก่า
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # ตรวจสอบว่ามีข้อมูลแผ่นดินไหวหรือไม่
        if data['features']:
            earthquake_info = data['features'][0]['properties']
            
            # ตรวจสอบว่าแผ่นดินไหวมีข้อมูลตำแหน่งหรือไม่
            if 'coordinates' in data['features'][0]['geometry']:
                latitude = data['features'][0]['geometry']['coordinates'][1]
                longitude = data['features'][0]['geometry']['coordinates'][0]
            else:
                latitude = "ไม่ระบุ"
                longitude = "ไม่ระบุ"
            
            # แปลงเวลา (timestamp) เป็นเวลาของประเทศไทย (UTC+7)
            timestamp = earthquake_info['time'] / 1000  # Convert milliseconds to seconds
            utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
            thailand_time = utc_time.astimezone(pytz.timezone('Asia/Bangkok'))

            return {
                "date": thailand_time.strftime('%Y-%m-%d'),  # วันที่
                "time": thailand_time.strftime('%H:%M:%S'),  # เวลา
                "magnitude": earthquake_info['mag'],
                "latitude": latitude,
                "longitude": longitude,
                "location": earthquake_info['place'],
            }
        else:
            print("No earthquake data available.")
            return None

    except requests.RequestException as e:
        print(f"Error fetching earthquake data: {e}")
        return None

def send_discord_alert(earthquake_info, webhook_url):
    message = (
        f"\n**แผ่นดินไหวแจ้งเตือน!**\n"
        f"📅 วันที่: {earthquake_info['date']}\n"
        f"⏰ เวลา: {earthquake_info['time']}\n"
        f"🌍 ขนาด: {earthquake_info['magnitude']} ริกเตอร์\n"
        f"📍 ตำแหน่ง: {earthquake_info['latitude']}, {earthquake_info['longitude']}\n"
        f"🏠 สถานที่: {earthquake_info['location']}"
    )
    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending Discord alert: {e}")

if __name__ == "__main__":
    DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1355214995771621457/PSC4Yv3mAhxwcTUvkkYDB8nQp7HEItkZaZp9nA4t_ZZ-NC3_sjjq-JxTGAusd-BmUSFn"
    earthquake_data = get_earthquake_data()
    if earthquake_data:
        send_discord_alert(earthquake_data, DISCORD_WEBHOOK_URL)
    else:
        print("ไม่พบข้อมูลแผ่นดินไหว")
