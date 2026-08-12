

def format_standard_station(data):
    c = data["conditions"]
    w = data["wind"]
    r = data["rain"]
    t = data["trends"]

    return (
        f"🪂 <b>{data['station'].upper()}</b>\n"
        f"🕐 {data['time']}\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"

        f"🌡️ <b>CONDITIONS</b>\n"
        f"Temperature: {c['temperature']}°C\n"
        f"Humidity: {c['humidity']}%\n"
        f"Pressure: {c['pressure']} hPa\n"
        f"Dew point: {c['dew_point']}°C\n"
        f"☁️ Cloud base: {c['cloud_base']} m\n\n"

        f"💨 <b>WIND</b>\n"
        f"Speed: {w['speed_ms']} m/s ({w['speed']} km/h)\n"
        f"Direction: {w['direction']} ({w['angle']}°)\n"
        f"Gusts: {w['gust_ms']} m/s ({w['gust']} km/h)\n"
        f"Maximum: {w['max_ms']} m/s ({w['max']} km/h)\n\n"

        f"📊 <b>AVERAGES</b>\n"
        f"15 min: {w['avg_15']['speed']} km/h "
        f"{w['avg_15']['direction']}\n"
        f"30 min: {w['avg_30']['speed']} km/h "
        f"{w['avg_30']['direction']}\n"
        f"60 min: {w['avg_60']['speed']} km/h "
        f"{w['avg_60']['direction']}\n\n"

        f"🌧️ <b>RAIN</b>\n"
        f"Current: {r['current']} mm\n"
        f"Last hour: {r['1h']} mm\n"
        f"Today: {r['day']} mm\n\n"

        f"📈 <b>TRENDS (1h)</b>\n"
        f"Temperature: {t['temperature']:+}°C\n"
        f"Pressure: {t['pressure']:+} hPa\n"
        f"Humidity: {t['humidity']:+}%\n"
        f"Dew point: {t['dew_point']:+}°C"
    )


def format_rajac(data):
    c = data["conditions"]
    w = data["wind"]
    r = data["rain"]
    a = data["alerts"]
    e = data["extras"]

    return (
        f"🪂 <b>RAJAC</b>\n"
        f"🕐 {data['time']}\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"

        f"🌡️ <b>CONDITIONS</b>\n"
        f"Temperature: {c['temperature']}°C\n"
        f"Humidity: {c['humidity']}%\n"
        f"Pressure: {c['pressure']} hPa\n"
        f"Dew point: {c['dew_point']}°C\n"
        f"Pressure trend: {c['bar_trend']}\n\n"

        f"💨 <b>WIND</b>\n"
        f"Speed: {w['speed_ms']} m/s ({w['speed']} km/h)\n"
        f"Direction: {w['angle']}°\n"
        f"Gusts: {w['gust_ms']} m/s ({w['gust']} km/h)\n"
        f"Gust change: {w['gust_delta_10min_ms']:+} m/s\n\n"

        f"🌧️ <b>RAIN</b>\n"
        f"Rate: {r['rate']} mm/h\n"
        f"Today: {r['day']} mm\n"
        f"24h: {r['last_24h']} mm\n\n"

        f"⚠️ <b>ALERTS</b>\n"
        f"{'🔴' if a['gust_alert'] else '🟢'} Gust alert\n"
        f"{'🔴' if a['storm_wind_alert'] else '🟢'} Storm wind\n"
        f"{'🔴' if a['pressure_drop_alert'] else '🟢'} Pressure drop\n"
        f"{'🔴' if a['sudden_rain_alert'] else '🟢'} Sudden rain\n\n"

        f"🥾 <b>EXTRAS</b>\n"
        f"Fog risk: {e['fog_risk']}\n"
        f"Trail: {e['trail_state']}\n"
        f"Hiking index: {e['hiking_index']}"
    )


def format_station(data):
    if data["station_id"] == 25:
        return format_rajac(data)

    return format_standard_station(data)
