from pyrogram import Client, filters
from pyrogram.types import Message
import os

VBV_FILE = "FILES/vbvbin.txt"

def load_vbv_data():
    """Load VBV BIN data from file into a dictionary"""
    vbv_data = {}
    if os.path.exists(VBV_FILE):
        with open(VBV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        bin_num = parts[0].strip()
                        status = parts[1].strip()
                        info = parts[2].strip()
                        vbv_data[bin_num] = {"status": status, "info": info}
    return vbv_data

@Client.on_message(filters.command("vbv"))
async def vbv_lookup(client, message: Message):
    """Lookup VBV/3D Secure status for a BIN"""
    if len(message.command) < 2:
        return await message.reply(
            "<pre>VBV Lookup ❌</pre>\n<b>Usage:</b> <code>/vbv 414720</code>",
            reply_to_message_id=message.id
        )
    
    bin_input = ''.join(filter(str.isdigit, message.command[1]))
    if len(bin_input) < 6:
        return await message.reply(
            "<pre>Invalid BIN ❌</pre>\n<b>BIN must be at least 6 digits.</b>",
            reply_to_message_id=message.id
        )
    
    bin_number = bin_input[:6]
    vbv_data = load_vbv_data()
    
    user_name = message.from_user.first_name
    profile = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>"
    
    if bin_number in vbv_data:
        data = vbv_data[bin_number]
        status = data["status"]
        info = data["info"]
        
        # Determine status emoji
        if "FALSE" in status.upper():
            status_emoji = "✅"
            status_text = "NON-VBV"
        else:
            status_emoji = "❌"
            status_text = "VBV"
        
        reply_text = f"""<pre>VBV Lookup Result {status_emoji}</pre>
━━━━━━━━━━━━━━━
<b>[•] BIN:</b> <code>{bin_number}</code>
<b>[•] Status:</b> <code>{status}</code>
<b>[•] Type:</b> <code>{status_text}</code>
<b>[•] Info:</b> <code>{info}</code>
━━━━━━━━━━━━━━━
<b>[•] Checked By:</b> {profile}"""
    else:
        reply_text = f"""<pre>VBV Lookup Result ⚠️</pre>
━━━━━━━━━━━━━━━
<b>[•] BIN:</b> <code>{bin_number}</code>
<b>[•] Status:</b> <code>Not Found in Database</code>
<b>[•] Info:</b> <code>Try checking with /bin for general info</code>
━━━━━━━━━━━━━━━
<b>[•] Checked By:</b> {profile}"""
    
    await message.reply(reply_text, reply_to_message_id=message.id, disable_web_page_preview=True)


@Client.on_message(filters.command("mvbv"))
async def mass_vbv_lookup(client, message: Message):
    """Mass VBV lookup for multiple BINs"""
    if len(message.command) < 2:
        return await message.reply(
            "<pre>Mass VBV Lookup ❌</pre>\n<b>Usage:</b> <code>/mvbv 414720 456789 ...</code>",
            reply_to_message_id=message.id
        )
    
    raw_input = message.text.split(None, 1)[1]
    
    # Extract BINs (6+ digits)
    import re
    candidates = re.findall(r'\b\d{6,16}\b', raw_input)
    bin_list = list({x[:6] for x in candidates if len(x) >= 6})
    
    if not bin_list:
        return await message.reply(
            "<pre>No valid BINs found ❌</pre>",
            reply_to_message_id=message.id
        )
    
    vbv_data = load_vbv_data()
    user_name = message.from_user.first_name
    profile = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>"
    
    results = []
    non_vbv_count = 0
    vbv_count = 0
    not_found = 0
    
    for bin_number in bin_list[:20]:  # Limit to 20
        if bin_number in vbv_data:
            data = vbv_data[bin_number]
            status = data["status"]
            
            if "FALSE" in status.upper():
                status_emoji = "✅"
                non_vbv_count += 1
            else:
                status_emoji = "❌"
                vbv_count += 1
            
            results.append(f"<code>{bin_number}</code> ➜ {status} {status_emoji}")
        else:
            not_found += 1
            results.append(f"<code>{bin_number}</code> ➜ Not Found ⚠️")
    
    reply_text = f"""<pre>Mass VBV Lookup 🔍</pre>
━━━━━━━━━━━━━━━
<b>Total:</b> {len(bin_list[:20])} | <b>NON-VBV:</b> {non_vbv_count} ✅ | <b>VBV:</b> {vbv_count} ❌ | <b>N/A:</b> {not_found}
━━━━━━━━━━━━━━━
""" + "\n".join(results) + f"""
━━━━━━━━━━━━━━━
<b>[•] Checked By:</b> {profile}"""
    
    await message.reply(reply_text, reply_to_message_id=message.id, disable_web_page_preview=True)


@Client.on_message(filters.command("nonvbv"))
async def get_nonvbv_bins(client, message: Message):
    """Get random NON-VBV BINs from database"""
    import random
    
    try:
        amount = int(message.command[1]) if len(message.command) > 1 else 5
        amount = min(amount, 20)  # Max 20
    except:
        amount = 5
    
    vbv_data = load_vbv_data()
    
    # Filter NON-VBV BINs
    non_vbv_bins = [
        (bin_num, data) for bin_num, data in vbv_data.items() 
        if "FALSE" in data["status"].upper()
    ]
    
    if not non_vbv_bins:
        return await message.reply(
            "<pre>No NON-VBV BINs found ❌</pre>",
            reply_to_message_id=message.id
        )
    
    selected = random.sample(non_vbv_bins, min(amount, len(non_vbv_bins)))
    
    user_name = message.from_user.first_name
    profile = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>"
    
    results = []
    for bin_num, data in selected:
        results.append(f"<code>{bin_num}</code> ➜ {data['info']}")
    
    reply_text = f"""<pre>NON-VBV BINs ✅</pre>
━━━━━━━━━━━━━━━
<b>Amount:</b> {len(selected)}
━━━━━━━━━━━━━━━
""" + "\n".join(results) + f"""
━━━━━━━━━━━━━━━
<b>[•] Requested By:</b> {profile}"""
    
    await message.reply(reply_text, reply_to_message_id=message.id, disable_web_page_preview=True)
