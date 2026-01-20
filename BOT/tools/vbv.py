from pyrogram import Client, filters
from pyrogram.types import Message
import os

VBV_FILE = "FILES/vbvbin.txt"

def load_vbv_database():
    """Load VBV BIN database from file"""
    vbv_data = {}
    if not os.path.exists(VBV_FILE):
        return vbv_data
    
    try:
        with open(VBV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 3:
                    bin_num = parts[0].strip()
                    status = parts[1].strip()
                    message = parts[2].strip()
                    vbv_data[bin_num] = {
                        "status": status,
                        "message": message
                    }
    except Exception as e:
        print(f"[VBV Load Error] {e}")
    
    return vbv_data

# Load VBV database once at startup
VBV_DATABASE = load_vbv_database()

def check_vbv(bin_number: str) -> dict:
    """Check if a BIN is in the VBV database"""
    bin_6 = bin_number[:6] if len(bin_number) >= 6 else bin_number
    
    if bin_6 in VBV_DATABASE:
        return {
            "found": True,
            "bin": bin_6,
            "status": VBV_DATABASE[bin_6]["status"],
            "message": VBV_DATABASE[bin_6]["message"]
        }
    
    return {
        "found": False,
        "bin": bin_6,
        "status": "Unknown",
        "message": "BIN not found in VBV database"
    }

@Client.on_message(filters.command("vbv"))
async def vbv_lookup(client, message: Message):
    """Check VBV status of a BIN"""
    if len(message.command) < 2:
        return await message.reply(
            "<pre>Usage ❌</pre>\n<b>/vbv {bin}</b>\n<code>Example: /vbv 414720</code>",
            reply_to_message_id=message.id
        )
    
    bin_input = ''.join(filter(str.isdigit, message.command[1]))
    
    if len(bin_input) < 6:
        return await message.reply(
            "<pre>Invalid BIN ❌</pre>\n<b>BIN must be at least 6 digits.</b>",
            reply_to_message_id=message.id
        )
    
    result = check_vbv(bin_input)
    
    user_name = message.from_user.first_name
    profile = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>"
    
    if result["found"]:
        # Determine emoji based on status
        status_emoji = "✅" if "FALSE" in result["status"].upper() else "❌"
        
        reply_text = f"""<pre>VBV Check Result 🔐</pre>
━ ━ ━ ━ ━━━ ━ ━ ━ ━
<b>⟐ BIN:</b> <code>{result['bin']}</code>
<b>⟐ Status:</b> <code>{result['status']}</code>
<b>⟐ Message:</b> <code>{result['message']}</code>
━ ━ ━ ━ ━━━ ━ ━ ━ ━
<b>⟐ Checked By:</b> {profile}
"""
    else:
        reply_text = f"""<pre>VBV Check Result 🔐</pre>
━ ━ ━ ━ ━━━ ━ ━ ━ ━
<b>⟐ BIN:</b> <code>{result['bin']}</code>
<b>⟐ Status:</b> <code>Not Found ⚠️</code>
<b>⟐ Message:</b> <code>BIN not in VBV database</code>
━ ━ ━ ━ ━━━ ━ ━ ━ ━
<b>⟐ Checked By:</b> {profile}
"""
    
    await message.reply(
        reply_text,
        reply_to_message_id=message.id,
        disable_web_page_preview=True
    )

@Client.on_message(filters.command("mvbv"))
async def mass_vbv_lookup(client, message: Message):
    """Check VBV status of multiple BINs"""
    if len(message.command) < 2:
        return await message.reply(
            "<pre>Usage ❌</pre>\n<b>/mvbv {bin1} {bin2} ...</b>\n<code>Example: /mvbv 414720 424242 453201</code>",
            reply_to_message_id=message.id
        )
    
    # Extract all BINs from the message
    raw_input = message.text.split(None, 1)[1]
    import re
    candidates = re.findall(r'\b\d{6,16}\b', raw_input)
    bin_list = list({x[:6] for x in candidates if len(x) >= 6})
    
    if not bin_list:
        return await message.reply(
            "<pre>No Valid BINs ❌</pre>\n<b>Each BIN must be at least 6 digits.</b>",
            reply_to_message_id=message.id
        )
    
    user_name = message.from_user.first_name
    profile = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>"
    
    results = []
    for bin_num in bin_list[:15]:  # Limit to 15 BINs
        result = check_vbv(bin_num)
        
        if result["found"]:
            status_emoji = "✅" if "FALSE" in result["status"].upper() else "❌"
            results.append(f"""<b>⟐ BIN:</b> <code>{result['bin']}</code>
<b>⟐ Status:</b> <code>{result['status']}</code>
<b>⟐ Message:</b> <code>{result['message']}</code>
━ ━ ━ ━ ━━━ ━ ━ ━ ━""")
        else:
            results.append(f"""<b>⟐ BIN:</b> <code>{result['bin']}</code>
<b>⟐ Status:</b> <code>Not Found ⚠️</code>
━ ━ ━ ━ ━━━ ━ ━ ━ ━""")
    
    reply_text = f"<pre>Mass VBV Check 🔐</pre>\n━ ━ ━ ━ ━━━ ━ ━ ━ ━\n" + "\n".join(results) + f"\n<b>⟐ Checked By:</b> {profile}"
    
    await message.reply(
        reply_text,
        reply_to_message_id=message.id,
        disable_web_page_preview=True
    )
