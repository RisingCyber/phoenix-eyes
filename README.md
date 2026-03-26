<div align="center">

```
██████╗ ██╗  ██╗ ██████╗ ███████╗███╗   ██╗██╗██╗  ██╗    ███████╗██╗   ██╗███████╗███████╗
██╔══██╗██║  ██║██╔═══██╗██╔════╝████╗  ██║██║╚██╗██╔╝    ██╔════╝╚██╗ ██╔╝██╔════╝██╔════╝
██████╔╝███████║██║   ██║█████╗  ██╔██╗ ██║██║ ╚███╔╝     █████╗   ╚████╔╝ █████╗  ███████╗
██╔═══╝ ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║██║ ██╔██╗     ██╔══╝    ╚██╔╝  ██╔══╝  ╚════██║
██║     ██║  ██║╚██████╔╝███████╗██║ ╚████║██║██╔╝ ██╗    ███████╗   ██║   ███████╗███████║
╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝    ╚══════╝   ╚═╝   ╚══════╝╚══════╝
```

**Multi-Layer OSINT Intelligence Platform**

![Python](https://img.shields.io/badge/Python-3.8+-00d4ff?style=flat-square&labelColor=0d1117)
![Layers](https://img.shields.io/badge/layers-7-39ff14?style=flat-square&labelColor=0d1117)
![Auth](https://img.shields.io/badge/API_keys-none_required-ff9500?style=flat-square&labelColor=0d1117)
![Size](https://img.shields.io/badge/size-2_files-bf5fff?style=flat-square&labelColor=0d1117)

</div>

---

## What is Phoenix Eyes?

Phoenix Eyes is a self-hosted, zero-authentication open-source intelligence (OSINT), Signal intelligence (SIGINT), Geospatial Intelligence (GEOINT) platform that aggregates seven live global data feeds into a single tactical interface.

It runs on a lightweight Python stdlib server (no pip installs required) that handles CORS proxying and static file serving, with a Leaflet.js base map as the rendering engine. 

Intelligence layers include live ADS-B air traffic fetched directly from adsb.fi (with automatic OpenSky Network fallback), global AIS marine vessel positions via VesselFinder, GPS and GNSS jamming interference maps from GPSJam.org, ground-based and LEO satellite RF interference heatmaps from Stanford SRI's RFI monitoring platform, real-time seismic activity from the USGS global earthquake feed, live traffic camera JPEG feeds from the NYC Department of Transportation (60 cameras, refreshing every 5 seconds), and a Windy.com wind and weather overlay that syncs to the current map view. Every layer is toggleable, the RFI and jamming date is user-selectable, and three base maps are available — CartoDB Dark, ESRI Satellite, and ESRI Terrain. The entire project ships as two files: server.py and templates/index.html. 

To run it, clone the repo and execute python3 server.py — thats it, no environment variables, no API keys, no build step, no dependencies beyond Python 3.8 and a browser.
---

## Intelligence Layers

| # | Layer | Source | How it works | Auth |
|---|-------|--------|--------------|------|
| 1 | ✈ **Air Traffic** | [adsb.fi](https://adsb.fi) + [OpenSky](https://opensky-network.org) | Direct CORS fetch, rendered as Leaflet markers | None |
| 2 | ⚓ **Marine Traffic** | [VesselFinder](https://vesselfinder.com) | JS widget in fullscreen modal | None |
| 3 | ⚡ **GPS Jamming** | [GPSJam](https://gpsjam.org) | Iframe modal, date-selectable | None |
| 4 | 📡 **RFI + LEO Jamming** | [Stanford SRI](https://rfi.stanford.edu) | Split-pane iframe (ground + satellite) | None |
| 5 | 🌍 **Earthquakes** | [USGS](https://earthquake.usgs.gov) | Direct GeoJSON fetch, Leaflet circles | None |
| 6 | 🌬 **Wind / Weather** | [Windy.com](https://windy.com) | Iframe overlay on Leaflet map | None |
| 7 | 📹 **Traffic Cameras** | [NYC DOT](https://webcams.nyctmc.org/api/cameras) | Live JPEG grid, 5s refresh, 60 cams | None |



# 1. Clone git clone https://github.com/RisingCyber/phoenix-eyes
cd phoenix-eyes-v2

# 2. unzip phoenix-eyes-v2.zip 

# 3. python3 server.py

# 4. Open
open http://localhost:8080   

(thats it, NO environment variables, no API keys, no build step, no dependencies)



Sources:
Air Traffic (adsb.fi global, OpenSky fallback)
Marine Traffic (VesselFinder widget, global zoom 3) 
GPS Jamming (GPSJam iframe, global zoom 2)
RFI + LEO (Stanford SRI, side-by-side modal)
Earthquakes (USGS global GeoJSON, all magnitudes)
Wind/Weather (Windy embed, syncs to current map view)
Traffic Cameras (NYC DOT, 60 live JPEGs, 5s refresh)
