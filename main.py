import requests
import cherrypy
import os
import json

# Pull from config.json
with open("config.json") as f:
    config = json.load(f)
    HA_URL = config["ha_url"]
    HA_TOKEN = config["ha_token"]
    TRACKER_ID = config["tracker_id"]
    BATTERY_ID = config["battery_id"]
    LOCK_ID = config["lock_id"]
    APP_ID = config["app_id"]
    WEB_PASSWORD = config.get("web_password", "admin")

class PuppyTracker(object):
    @cherrypy.expose
    def index(self):
        if not cherrypy.session.get('logged_in'):
            return open("login.html")
        return open("index.html")

    @cherrypy.expose
    def login(self, password):
        if password == WEB_PASSWORD:
            cherrypy.session['logged_in'] = True
            raise cherrypy.HTTPRedirect("/")
        return "Invalid Password. <a href='/'>Try again</a>"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def data(self):
        if not cherrypy.session.get('logged_in'):
            cherrypy.response.status = 401
            return {"error": "Unauthorized"}

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
            "is_locked": lock_info.get("state", "off")
        }

if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
    })

    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.sessions.storage_type': "ram",
            'tools.sessions.timeout': 43200, # 30 Days
        },
        # This part ensures the app can see the manifest.json file
        '/manifest.json': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.abspath("manifest.json")
        }
    }
    
    cherrypy.quickstart(PuppyTracker(), '/', conf)