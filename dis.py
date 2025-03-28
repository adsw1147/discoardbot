import requests
from datetime import datetime
import pytz

def get_earthquake_data():
    # URL สำหรับดึงข้อมูลแผ่นดินไหว
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "limit": 10,  # จำนวนข้อมูลแผ่นดินไหวที่ดึงมา
        "orderby": "time",
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['features']:
            earthquake_info_list = []
            for event in data['features']:
                earthquake_info = event['properties']
                coordinates = event['geometry']['coordinates']
                latitude = coordinates[1]
                longitude = coordinates[0]

                # กรองข้อมูลแผ่นดินไหวที่เกิดในประเทศไทย (พิกัด Latitude และ Longitude)
                if 6.0 <= latitude <= 20.0 and 97.0 <= longitude <= 106.0:
                    timestamp = earthquake_info['time'] / 1000
                    utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
                    thailand_time = utc_time.astimezone(pytz.timezone('Asia/Bangkok'))

                    earthquake_info_list.append({
                        "date": thailand_time.strftime('%Y-%m-%d'),
                        "time": thailand_time.strftime('%H:%M:%S'),
                        "magnitude": earthquake_info['mag'],
                        "latitude": latitude,
                        "longitude": longitude,
                        "location": earthquake_info['place'],
                    })
            return earthquake_info_list

        else:
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
    DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"
    earthquake_data = get_earthquake_data()
    if earthquake_data:
        for earthquake in earthquake_data:
            send_discord_alert(earthquake, DISCORD_WEBHOOK_URL)
    else:
        print("ไม่พบข้อมูลแผ่นดินไหวในประเทศไทย")
