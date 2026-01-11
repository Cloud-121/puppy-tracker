import requests
import cherrypy
import os
import json

#pull from config.json
with open("config.json") as f:
    config = json.load(f)

    HA_URL = config["ha_url"]
    HA_TOKEN = config["ha_token"]

    TRACKER_ID = config["tracker_id"]
    BATTERY_ID = config["battery_id"]
    LOCK_ID = config["lock_id"]
    APP_ID = config["app_id"]

class PuppyTracker(object):
    @cherrypy.expose
    def index(self):
        return open("index.html")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def data(self):
        headers = {"Authorization": f"Bearer {HA_TOKEN}"}
        
        def fetch_ha(eid):
            try:
                r = requests.get(f"{HA_URL}/api/states/{eid}", headers=headers)
                return r.json()
            except: return {}

        tracker = fetch_ha(TRACKER_ID)
        battery = fetch_ha(BATTERY_ID)
        app_info = fetch_ha(APP_ID)
        lock_info = fetch_ha(LOCK_ID)
        
        attr = tracker.get("attributes", {})
        
        return {
            "name": "Puppy",
            "lat": attr.get("latitude"),
            "lon": attr.get("longitude"),
            "battery": battery.get("state", "0"),
            "app": app_info.get("state", "None"),
            "is_locked": lock_info.get("state", "off") # 'on' usually means locked
        }

if __name__ == '__main__':
    cherrypy.quickstart(PuppyTracker())