import sys
from __future__ import annotations
import httpx
from datetime import datetime
import unicodedata

print(sys.version)


def format_time(value) -> str:
    if not value:
        return "N/A"

    dt = datetime.fromisoformat(value)

    return dt.strftime("%d-%m-%Y %H:%M:%S")


def normalize_station_name(name: str) -> str:
    name = name.lower().strip()

    # Allow users to omit Serbian diacritics
    replacements = {
        "š": "s",
        "đ": "dj",
        "č": "c",
        "ć": "c",
        "ž": "z",
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    return " ".join(name.split())


def get_station_id(name: str) -> int | None:
    normalized = normalize_station_name(name)

    all_stations = {
        **stations,
        25: "Rajac",
    }

    for station_id, station_name in all_stations.items():
        if normalize_station_name(station_name) == normalized:
            return station_id

    return None


stations = {
    14: "Zlatibor-Vojska",
    16: "Vršac-Kula",
    24: "Stolovi",
    26: "Višegradska stena",
    27: "Titelski breg",
    30: "Veliki Radinci",
    33: "Fruška gora",
    35: "Sekulića brdo",
    46: "Klokoč",
}

CUSTOM_STATIONS = {
    25: {
        "name": "Rajac",
        "url": "https://piorajac.rs/amsrajac/api.php?nocache=1",
    }
}


def rf(value) -> float | None:
    if value is None:
        return None

    return round(float(value), 2)


def kmh_to_ms(value):
    if value is None:
        return None

    return round(float(value) / 3.6, 1)


async def get_rajac_data():
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(CUSTOM_STATIONS[25]["url"])
        resp.raise_for_status()

        data = resp.json()

    v = data["values"]
    d = data["derived"]
    f = data["rapid_change_flags"]
    deltas = data["nowcast_meta"]["recent_deltas"]

    return {
        "station": "Rajac",
        "station_id": 25,
        "time": format_time(data["nowcast_meta"]["source_observed_at"]),
        "conditions": {
            "temperature": rf(v["temp"]),
            "humidity": rf(v["humidity"]),
            "pressure": rf(v["pressure_hpa"]),
            "dew_point": rf(v["dew_point"]),
            "bar_trend": v["bar_trend"],
        },

        "wind": {
            "speed": rf(v["wind_speed"]),
            "speed_ms": kmh_to_ms(v["wind_speed"]),

            "angle": rf(v["wind_dir"]),

            "gust": rf(v["wind_gust"]),
            "gust_ms": kmh_to_ms(v["wind_gust"]),

            "gust_delta_10min": rf(deltas["gust_10min"]),
            "gust_delta_10min_ms": kmh_to_ms(deltas["gust_10min"]),
        },

        "rain": {
            "rate": rf(v["rain_rate"]),
            "day": rf(v["rain_day"]),
            "last_24h": rf(v["rain_24h"]),
        },

        "alerts": {
            "gust_alert": f["gust_alert"],
            "storm_wind_alert": f["storm_wind_alert"],
            "pressure_drop_alert": f["pressure_drop_alert"],
            "sudden_rain_alert": f["sudden_rain_alert"],
        },

        "extras": {
            "fog_risk": d["fog_risk"],
            "trail_state": d["trail_state"],
            "hiking_index": d["hiking_index"],
        },
    }


async def get_station_data(station_id: int):
    if station_id == 25:
        return await get_rajac_data()

    async with httpx.AsyncClient(timeout=10) as client:

        now = await client.get(
            f"https://flumen.club/wp/data/rest.php/Now"
            f"?filter=Station,eq,{station_id}"
        )

        rain_trend = await client.get(
            f"https://flumen.club/wp/zbelacRain.php?station={station_id}"
        )

        avg15 = await client.get(
            f"https://flumen.club/wp/averageDirection.php"
            f"?station={station_id}&interval=15"
        )

        avg30 = await client.get(
            f"https://flumen.club/wp/averageDirection.php"
            f"?station={station_id}&interval=30"
        )

        avg60 = await client.get(
            f"https://flumen.club/wp/averageDirection.php"
            f"?station={station_id}&interval=60"
        )

        interval15 = await client.get(
            f"https://flumen.club/wp/data/rest.php/Interval15"
            f"?filter=Station,eq,{station_id}"
        )

        interval30 = await client.get(
            f"https://flumen.club/wp/data/rest.php/Interval30"
            f"?filter=Station,eq,{station_id}"
        )

        interval60 = await client.get(
            f"https://flumen.club/wp/data/rest.php/Interval60"
            f"?filter=Station,eq,{station_id}"
        )

        for response in (
                now,
                rain_trend,
                avg15,
                avg30,
                avg60,
                interval15,
                interval30,
                interval60,
        ):
            response.raise_for_status()

    now_data = now.json()["Now"]
    now_rec = dict(
        zip(now_data["columns"], now_data["records"][0])
    )

    rt = rain_trend.json()[0]

    i15_data = interval15.json()["Interval15"]
    i15_rec = dict(
        zip(i15_data["columns"], i15_data["records"][0])
    )

    i30_data = interval30.json()["Interval30"]
    i30_rec = dict(
        zip(i30_data["columns"], i30_data["records"][0])
    )

    i60_data = interval60.json()["Interval60"]
    i60_rec = dict(
        zip(i60_data["columns"], i60_data["records"][0])
    )

    return {
        "station": stations[station_id],
        "station_id": station_id,
        "time": format_time(now_rec["SEND_TIME"]),

        "conditions": {
            "temperature": rf(now_rec["TEMPERATURE"]),
            "humidity": rf(now_rec["MOIST"]),
            "pressure": rf(now_rec["PRESSURE"]),
            "dew_point": rf(now_rec["dewp"]),
            "cloud_base": rf(now_rec["CLOUD"]),
            "sun": rf(now_rec["SUN"]),
        },

        "wind": {
            "speed": rf(now_rec["WIND_SP"]),
            "speed_ms": kmh_to_ms(now_rec["WIND_SP"]),
            "direction": now_rec["WIND_DIR"],
            "angle": rf(now_rec["WIND_ANG"]),
            "gust": rf(now_rec["WIND_GUST"]),
            "gust_ms": kmh_to_ms(now_rec["WIND_GUST"]),
            "max": rf(now_rec["WIND_MAX"]),
            "max_ms": kmh_to_ms(now_rec["WIND_MAX"]),

            "avg_15": {
                "speed": rf(i15_rec["AVG(`WIND_SP`)"]),
                "speed_ms": kmh_to_ms(i15_rec["AVG(`WIND_SP`)"]),
                "gust": rf(i15_rec["AVG(`WIND_GUST`)"]),
                "gust_ms": kmh_to_ms(i15_rec["AVG(`WIND_GUST`)"]),
                "max": rf(i15_rec["AVG(`WIND_MAX`)"]),
                "max_ms": kmh_to_ms(i15_rec["AVG(`WIND_MAX`)"]),
                "direction": avg15.json()[0]["WIND_DIR"],
            },

            "avg_30": {
                "speed": rf(i30_rec["AVG(`WIND_SP`)"]),
                "speed_ms": kmh_to_ms(i30_rec["AVG(`WIND_SP`)"]),
                "gust": rf(i30_rec["AVG(`WIND_GUST`)"]),
                "gust_ms": kmh_to_ms(i30_rec["AVG(`WIND_GUST`)"]),
                "max": rf(i30_rec["AVG(`WIND_MAX`)"]),
                "max_ms": kmh_to_ms(i30_rec["AVG(`WIND_MAX`)"]),
                "direction": avg30.json()[0]["WIND_DIR"],
            },

            "avg_60": {
                "speed": rf(i60_rec["AVG(`WIND_SP`)"]),
                "speed_ms": kmh_to_ms(i60_rec["AVG(`WIND_SP`)"]),
                "gust": rf(i60_rec["AVG(`WIND_GUST`)"]),
                "gust_ms": kmh_to_ms(i60_rec["AVG(`WIND_GUST`)"]),
                "max": rf(i60_rec["AVG(`WIND_MAX`)"]),
                "max_ms": kmh_to_ms(i60_rec["AVG(`WIND_MAX`)"]),
                "direction": avg60.json()[0]["WIND_DIR"],
            },
        },

        "rain": {
            "current": rf(now_rec["RAIN"]),
            "1h": rf(rt["rainHour"]),
            "day": rf(rt["rainDay"]),
        },

        "trends": {
            "temperature": rf(rt["diff_Temp_hour"]),
            "pressure": rf(rt["diff_Pressure_hour"]),
            "humidity": rf(rt["diff_MOIST_hour"]),
            "cloud": rf(rt["diff_CLOUD_hour"]),
            "dew_point": rf(rt["diff_D_POINT_hour"]),
            "heat_index": rf(rt["diff_HEAT_INDEX_hour"]),
        },
    }
