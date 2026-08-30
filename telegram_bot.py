from __future__ import annotations

import os
import time
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
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

REFRESH_COOLDOWN_SECONDS = 60
_last_refresh: dict[tuple[int, int], float] = {}  # (chat_id, station_id) -> timestamp


def refresh_keyboard(station_id: int) -> InlineKeyboardMarkup:
    """Build the inline 'Refresh' button attached under every station message."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_{station_id}")]
    ])


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
                    reply_markup=refresh_keyboard(station_id),
                )
                return

            except Exception as e:
                await update.message.reply_text(
                    "❌ Could not retrieve weather data.\n"
                    "      Station is not available.😕\n\n"
                    "⚠︎ Battery or SIM out of function!🪫",
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
            reply_markup=refresh_keyboard(station_id),
        )

    except Exception as e:
        await update.message.reply_text(
            "❌ Could not retrieve weather data.\n"
            "      Station is not available.😕\n\n"
            "Battery or SIM out of function!🪫",
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
            reply_markup=refresh_keyboard(25),
        )

    except Exception as e:
        await update.message.reply_text(
            "❌ Could not retrieve Rajac data.\n"
            "      Station is not available.😕\n\n"
            "Battery or SIM out of function!🪫",
            parse_mode="HTML",
        )


async def refresh_station(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Handle taps on the Refresh button -- re-fetch the same station's
    data and update the existing message in place, rather than sending a
    new one. Rate-limited per (chat, station) so rapid taps don't hammer
    the upstream weather APIs."""
    query = update.callback_query
    station_id = int(query.data.replace("refresh_", ""))
    chat_id = update.effective_chat.id

    key = (chat_id, station_id)
    now = time.time()
    elapsed = now - _last_refresh.get(key, 0)

    if elapsed < REFRESH_COOLDOWN_SECONDS:
        wait_left = int(REFRESH_COOLDOWN_SECONDS - elapsed)
        await query.answer(
            f"⏳ Please wait {wait_left}s before refreshing again.",
            show_alert=False,
        )
        return

    try:
        data = await get_station_data(station_id)
        message = format_station(data)

        await query.edit_message_text(
            message,
            parse_mode="HTML",
            reply_markup=refresh_keyboard(station_id),
        )
        _last_refresh[key] = now
        await query.answer("Updated")

    except Exception as e:
        # Message body stays as-is if the refresh fails -- just show a
        # transient alert rather than replacing good data with an error.
        await query.answer(f"Wait for a bot to set up! ⚙️🛠️\n"
                            "You can refresh in 20 seconds!️", show_alert=True)


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
    app.add_handler(CallbackQueryHandler(refresh_station, pattern=r"^refresh_\d+$"))

    print("🪂 Telegram bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()