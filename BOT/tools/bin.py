from pyrogram import Client, filters
from TOOLS.getbin import get_bin_details
import re
import os

# VBV BIN data file
VBVBIN_FILE = "FILES/vbvbin.txt"

def load_vbv_data():
    """Load VBV BIN data from file"""
    vbv_data = {}
    if os.path.exists(VBVBIN_FILE):
        try:
            with open(VBVBIN_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 3:
                            bin_num = parts[0].strip()
                            vbv_status = parts[1].strip()
                            vbv_msg = parts[2].strip()
                            vbv_data[bin_num] = {"status": vbv_status, "message": vbv_msg}
        except Exception as e:
            print(f"Error loading VBV data: {e}")
    return vbv_data

VBV_DATA = load_vbv_data()

@Client.on_message(filters.command("bin"))
async def bin_lookup(client, message):
    if len(message.command) < 2:
        return await message.reply("Please provide a BIN or card number.", reply_to_message_id=message.id)

    bin_input = ''.join(filter(str.isdigit, message.command[1]))
    if len(bin_input) < 6:
        return await message.reply("Invalid BIN. Must be at least 6 digits.", reply_to_message_id=message.id)

    bin_number = bin_input[:6]
    data = get_bin_details(bin_number)

    if not data:
        return await message.reply("No info found for this BIN.", reply_to_message_id=message.id)

    user_name = message.from_user.first_name
    profile = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>"

    reply_text = f"""𝐁𝐢𝐧 𝐋𝐨𝐨𝐤𝐮𝐩 𝐑𝐞𝐬𝐮𝐥𝐭 🔍
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
𝐁𝐢𝐧 ➜ <code>{data['bin']}</code>
𝗜𝗻𝗳𝗼 ➜ <code>{data['vendor']}-{data['type']}-{data['level'] or "Unknown"}</code>
𝗜𝘀𝘀𝘂𝗲𝗿 ➜ <code>{data['bank']}</code> 🏛
𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ➜ <code>{data['country']} {data['flag']}</code>
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 ➜ {profile}
"""

    await client.send_message(
        chat_id=message.chat.id,
        text=reply_text,
        reply_to_message_id=message.id,
        disable_web_page_preview=True
    )

@Client.on_message(filters.command("mbin"))
async def mass_bin_lookup(client, message):
    if len(message.command) < 2:
        return await message.reply("Please provide one or more BINs or card numbers.", reply_to_message_id=message.id)

    raw_input = message.text.split(None, 1)[1]

    # Extract 16+ digit card numbers or standalone BINs or BINs from cc|mm|yy|cvv formats
    candidates = re.findall(r'\b\d{6,16}\b', raw_input)
    bin_list = list({x[:6] for x in candidates if len(x) >= 6})

    if not bin_list:
        return await message.reply("No valid BINs found. Each BIN must be at least 6 digits.", reply_to_message_id=message.id)

    user_name = message.from_user.first_name
    profile = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>"

    results = []
    for bin_number in bin_list[:20]:  # Optional limit to 20
        data = get_bin_details(bin_number)
        if not data:
            results.append(f"""𝐁𝐢𝐧 ➜ <code>{bin_number}</code>\n𝗦𝘁𝗮𝘁𝘂𝘀 ➜ <code>Not Found ❌</code>\n━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━""")
            continue

        results.append(f"""𝐁𝐢𝐧 𝐋𝐨𝐨𝐤𝐮𝐩 𝐑𝐞𝐬𝐮𝐥𝐭 🔍
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
𝐁𝐢𝐧 ➜ <code>{data['bin']}</code>
𝗜𝗻𝗳𝗼 ➜ <code>{data['vendor']}-{data['type']}-{data['level'] or "Unknown"}</code>
𝗜𝘀𝘀𝘂𝗲𝗿 ➜ <code>{data['bank']}</code> 🏛
𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ➜ <code>{data['country']} {data['flag']}</code>
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━""")

    reply_text = "\n".join(results) + f"\n𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 ➜ {profile}"

    await client.send_message(
        chat_id=message.chat.id,
        text=reply_text,
        reply_to_message_id=message.id,
        disable_web_page_preview=True
    )


@Client.on_message(filters.command(["vbv", "3ds"]))
async def vbv_bin_lookup(client, message):
    """Check VBV/3DS status of a BIN"""
    if len(message.command) < 2:
        return await message.reply(
            "<pre>VBV Lookup ❌</pre>\n<b>Usage:</b> <code>/vbv {bin}</code>",
            reply_to_message_id=message.id
        )

    bin_input = ''.join(filter(str.isdigit, message.command[1]))
    if len(bin_input) < 6:
        return await message.reply(
            "<pre>Invalid BIN ❌</pre>\n<b>Must be at least 6 digits.</b>",
            reply_to_message_id=message.id
        )

    bin_number = bin_input[:6]
    user_name = message.from_user.first_name
    profile = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>"

    # Check VBV data
    vbv_info = VBV_DATA.get(bin_number)
    
    if not vbv_info:
        return await message.reply(
            f"<pre>VBV Lookup Result 🔍</pre>\n━━━━━━━━━━━━━━━\n<b>𝐁𝐢𝐧:</b> <code>{bin_number}</code>\n<b>𝗦𝘁𝗮𝘁𝘂𝘀:</b> <code>Not Found ❓</code>\n━━━━━━━━━━━━━━━\n<b>𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆:</b> {profile}",
            reply_to_message_id=message.id
        )

    # Get BIN details too
    bin_data = get_bin_details(bin_number)
    bin_info_text = ""
    if bin_data:
        bin_info_text = f"""<b>𝗜𝗻𝗳𝗼:</b> <code>{bin_data['vendor']}-{bin_data['type']}-{bin_data['level'] or "Unknown"}</code>
<b>𝗜𝘀𝘀𝘂𝗲𝗿:</b> <code>{bin_data['bank']}</code> 🏛
<b>𝗖𝗼𝘂𝗻𝘁𝗿𝘆:</b> <code>{bin_data['country']} {bin_data['flag']}</code>
"""

    reply_text = f"""<pre>VBV Lookup Result 🔍</pre>
━━━━━━━━━━━━━━━
<b>𝐁𝐢𝐧:</b> <code>{bin_number}</code>
<b>𝟯𝗗𝗦:</b> <code>{vbv_info['status']}</code>
<b>𝗠𝗲𝘀𝘀𝗮𝗴𝗲:</b> <code>{vbv_info['message']}</code>
{bin_info_text}━━━━━━━━━━━━━━━
<b>𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆:</b> {profile}"""

    await client.send_message(
        chat_id=message.chat.id,
        text=reply_text,
        reply_to_message_id=message.id,
        disable_web_page_preview=True
    )


@Client.on_message(filters.command("mvbv"))
async def mass_vbv_lookup(client, message):
    """Mass VBV/3DS lookup for multiple BINs"""
    if len(message.command) < 2:
        return await message.reply(
            "<pre>Mass VBV Lookup ❌</pre>\n<b>Usage:</b> <code>/mvbv {bin1} {bin2} ...</code>",
            reply_to_message_id=message.id
        )

    raw_input = message.text.split(None, 1)[1]
    candidates = re.findall(r'\b\d{6,16}\b', raw_input)
    bin_list = list({x[:6] for x in candidates if len(x) >= 6})

    if not bin_list:
        return await message.reply(
            "<pre>Invalid BINs ❌</pre>\n<b>No valid BINs found. Each must be at least 6 digits.</b>",
            reply_to_message_id=message.id
        )

    user_name = message.from_user.first_name
    profile = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>"

    results = []
    for bin_number in bin_list[:20]:  # Limit to 20
        vbv_info = VBV_DATA.get(bin_number)
        if not vbv_info:
            results.append(f"<b>𝐁𝐢𝐧:</b> <code>{bin_number}</code> | <code>Not Found ❓</code>")
        else:
            results.append(f"<b>𝐁𝐢𝐧:</b> <code>{bin_number}</code> | <code>{vbv_info['status']}</code>")

    reply_text = f"""<pre>Mass VBV Lookup 🔍</pre>
━━━━━━━━━━━━━━━
""" + "\n".join(results) + f"""
━━━━━━━━━━━━━━━
<b>𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆:</b> {profile}"""

    await client.send_message(
        chat_id=message.chat.id,
        text=reply_text,
        reply_to_message_id=message.id,
        disable_web_page_preview=True
    )