import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from weather import get_station_data, stations
from formatter import format_station

load_dotenv()


TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🪂 <b>Local Meteo Bot</b>\n\n"
        "Available commands:\n\n"
        "/stations - list all stations\n"
        "/station ID - get station weather\n"
        "/rajac - get Rajac weather",
        parse_mode="HTML",
    )


async def station(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/station 33"
        )
        return

    try:
        station_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ Station ID must be a number."
        )
        return

    if station_id not in stations and station_id != 25:
        await update.message.reply_text(
            "❌ Unknown station."
        )
        return

    try:
        data = await get_station_data(station_id)

        message = format_station(data)

        await update.message.reply_text(
            message,
            parse_mode="HTML",
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error getting weather data:\n{e}"
        )


async def rajac(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        data = await get_station_data(25)

        message = format_station(data)

        await update.message.reply_text(
            message,
            parse_mode="HTML",
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error getting Rajac data:\n{e}"
        )


async def all_stations(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    message = "🪂 <b>LOCAL METEO</b>\n"
    message += "━━━━━━━━━━━━━━━━━━\n\n"

    all_ids = list(stations.keys()) + [25]

    for station_id in all_ids:

        try:
            data = await get_station_data(station_id)

            c = data["conditions"]
            w = data["wind"]

            message += (
                f"📍 <b>{data['station']}</b>\n"
                f"🌡️ {c['temperature']}°C  "
                f"💨 {w['speed']} km/h\n"
                f"💨 Gusts: {w['gust']} km/h\n"
                f"🌧️ Rain: "
            )

            if station_id == 25:
                message += f"{data['rain']['rate']} mm/h\n\n"
            else:
                message += f"{data['rain']['current']} mm\n\n"

        except Exception:
            message += (
                f"📍 <b>{stations.get(station_id, 'Rajac')}</b>\n"
                f"❌ Data unavailable\n\n"
            )

    await update.message.reply_text(
        message,
        parse_mode="HTML",
    )


def main():

    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is not set."
        )

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("station", station))
    app.add_handler(CommandHandler("stations", all_stations))
    app.add_handler(CommandHandler("rajac", rajac))

    print("Telegram bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()
