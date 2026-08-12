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
BOT_USERNAME = os.getenv("BOT_USERNAME")


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    # Handle clickable station links
    if context.args:
        argument = context.args[0]

        if argument.startswith("station_"):
            try:
                station_id = int(
                    argument.replace("station_", "")
                )

                data = await get_station_data(station_id)
                message = format_station(data)

                await update.message.reply_text(
                    message,
                    parse_mode="HTML",
                )
                return

            except Exception as e:
                await update.message.reply_text(
                    "❌ Could not retrieve weather data.\n"
                    "      Station is not available.😕\n\n"
                    f"<code>*{e}</code>",
                    parse_mode="HTML",
                )
                return

    # Normal /start message
    message = (
        "🇷🇸 <b>Serbian Local Meteo Assistant</b> 🪂\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Get current weather data from small\n"
        "local meteorological stations.\n\n"
        "<b>Commands:</b>\n\n"
        "/stations - list available stations\n"
        "/station NAME - get station weather\n\n"
        "<b>Example:</b>\n"
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
            "❌ Could not retrieve weather data.\n"
            "      Station is not available.😕\n\n"
            f"<code>*{e}</code>",
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
            "❌ Could not retrieve Rajac data.\n"
            "      Station is not available.😕\n\n"
            f"<code>*{e}</code>",
            parse_mode="HTML",
        )


async def station_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = (
        "🪂 <b>AVAILABLE STATIONS</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Click on location to get data.\n\n"
    )

    for station_id, name in stations.items():
        message += (
            f'📍 <a href="https://t.me/{BOT_USERNAME}'
            f'?start=station_{station_id}">{name}</a>\n\n'
        )

    message += (
        f'📍 <a href="https://t.me/{BOT_USERNAME}'
        f'?start=station_25">Rajac</a>\n'
    )

    await update.message.reply_text(
        message,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


def main():
    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is not set."
        )

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stations", station_list))
    app.add_handler(CommandHandler("station", station))
    app.add_handler(CommandHandler("rajac", rajac))

    print("🪂 Telegram bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()
