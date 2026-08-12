import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from weather import (
    get_station_data,
    get_station_id,
    stations,
)

from formatter import format_station

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = (
        "🇷🇸 <b>Serbian Local Meteo Assistant</b> 🪂\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Get current weather data from small\n"
        "local meteorological stations.\n\n"
        "<b>Commands:</b>\n\n"
        "/stations - list available stations\n"
        "/station NAME - get station weather\n"
        "Example:\n"
        "/station Fruška gora\n"
        "/station fruska gora"
    )

    await update.message.reply_text(
        message,
        parse_mode="HTML",
    )


async def station(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not context.args:
        await update.message.reply_text(
            "❌ Please specify a station.\n\n"
            "Example:\n"
            "/station Fruška gora\n\n"
            "Use /stations to see all available stations."
        )
        return

    station_name = " ".join(context.args)

    station_id = get_station_id(station_name)

    if station_id is None:
        await update.message.reply_text(
            f"❌ Station not found: <b>{station_name}</b>\n\n"
            "Use /stations to see available stations.",
            parse_mode="HTML",
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
            "❌ Could not retrieve weather data.\n\n"
            f"<code>{e}</code>",
            parse_mode="HTML",
        )


async def rajac(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        data = await get_station_data(25)

        message = format_station(data)

        await update.message.reply_text(
            message,
            parse_mode="HTML",
        )

    except Exception as e:
        await update.message.reply_text(
            "❌ Could not retrieve Rajac data.\n\n"
            f"<code>{e}</code>",
            parse_mode="HTML",
        )


async def station_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = (
        "🪂 <b>AVAILABLE STATIONS</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
    )

    for station_id, name in stations.items():
        message += (
            f"📍 <b>{name}</b>\n"
            f"/station {name}\n\n"
        )

    message += (
        "📍 <b>Rajac</b>\n"
        "/station Rajac\n"
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

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("stations", station_list)
    )

    app.add_handler(
        CommandHandler("station", station)
    )

    app.add_handler(
        CommandHandler("rajac", rajac)
    )

    print("🪂 Telegram bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()
