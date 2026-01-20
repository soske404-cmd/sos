# from pyrogram import Client, filters
# from pyrogram.types import Message
# import json, re, os, asyncio, httpx

# PROXY_FILE = "DATA/proxy.json"

# def load_proxies():
#     return json.load(open(PROXY_FILE)) if os.path.exists(PROXY_FILE) else {}

# def save_proxies(data):
#     with open(PROXY_FILE, "w") as f:
#         json.dump(data, f, indent=2)

# def normalize_proxy(proxy_raw: str) -> str:
#     proxy_raw = proxy_raw.strip()

#     # 1. Already full proxy URL
#     if proxy_raw.startswith("http://") or proxy_raw.startswith("https://"):
#         return proxy_raw

#     # 2. Format: USER:PASS@HOST:PORT
#     match1 = re.fullmatch(r"(.+?):(.+?)@([a-zA-Z0-9\.\-]+):(\d+)", proxy_raw)
#     if match1:
#         user, pwd, host, port = match1.groups()
#         return f"http://{user}:{pwd}@{host}:{port}"

#     # 3. Format: HOST:PORT:USER:PASS
#     match2 = re.fullmatch(r"([a-zA-Z0-9\.\-]+):(\d+):(.+?):(.+)", proxy_raw)
#     if match2:
#         host, port, user, pwd = match2.groups()
#         return f"http://{user}:{pwd}@{host}:{port}"

#     return None

# async def get_ip(proxy_url):
#     try:
#         transport = httpx.AsyncHTTPTransport(proxy=proxy_url)
#         async with httpx.AsyncClient(transport=transport, timeout=10) as client:
#             res = await client.get("https://ipinfo.io/json")
#             if res.status_code == 200:
#                 return res.json().get("ip"), None
#             return None, res.status_code
#     except Exception as e:
#         return None, str(e)

# @Client.on_message(filters.command("setpx") & filters.private)
# async def set_proxy(client, message: Message):
#     if len(message.command) < 2:
#         return await message.reply("❌ Format: `/setpx proxy`", quote=True)

#     raw_proxy = message.text.split(maxsplit=1)[1].strip()
#     proxy_url = normalize_proxy(raw_proxy)

#     if not proxy_url:
#         return await message.reply("❌ Invalid proxy format.\nSupported:\n- IP:PORT:USER:PASS\n- USER:PASS@IP:PORT\n- Full proxy link", quote=True)

#     msg = await message.reply("⏳ Checking proxy quality...", quote=True)

#     ip1, err1 = await get_ip(proxy_url)
#     await asyncio.sleep(2)
#     ip2, err2 = await get_ip(proxy_url)

#     if not ip1 or not ip2:
#         err_msg = err1 or err2 or "Unknown error"
#         return await msg.edit(f"❌ Your proxy failed to connect.\n**Error:** `{err_msg}`")

#     if ip1 == ip2:
#         return await msg.edit(f"⚠️ Proxy connected, but both IPs are the same:\n`{ip1}`\n\nThis is **not a high-quality proxy**. Try rotating/resi proxy.")

#     # Save proxy for user
#     user_id = str(message.from_user.id)
#     data = load_proxies()
#     data[user_id] = proxy_url
#     save_proxies(data)

#     await msg.edit(f"✅ Proxy saved successfully!\n\n🔁 Rotated IPs:\n- `{ip1}`\n- `{ip2}`")

# def get_proxy(user_id: int) -> str | None:

#     if not os.path.exists(PROXY_FILE):
#         return None

#     try:
#         data = json.load(open(PROXY_FILE))
#         return data.get(str(user_id))
#     except Exception:
#         return None

from pyrogram import Client, filters
from pyrogram.types import Message
import json, re, os, asyncio, httpx, random, csv

PROXY_FILE = "DATA/proxy.json"
PROXY_CSV_FILE = "FILES/proxy.csv"

def load_proxy_csv():
    """Load proxies from CSV file"""
    proxies = []
    if os.path.exists(PROXY_CSV_FILE):
        try:
            with open(PROXY_CSV_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    proxies.append(row)
        except Exception as e:
            print(f"Error loading proxy CSV: {e}")
    return proxies

PROXY_LIST = load_proxy_csv()

def load_proxies():
    return json.load(open(PROXY_FILE)) if os.path.exists(PROXY_FILE) else {}

def save_proxies(data):
    with open(PROXY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def normalize_proxy(proxy_raw: str) -> str:
    proxy_raw = proxy_raw.strip()

    # 1. Already full proxy URL
    if proxy_raw.startswith("http://") or proxy_raw.startswith("https://"):
        return proxy_raw

    # 2. Format: USER:PASS@HOST:PORT
    match1 = re.fullmatch(r"(.+?):(.+?)@([a-zA-Z0-9\.\-]+):(\d+)", proxy_raw)
    if match1:
        user, pwd, host, port = match1.groups()
        return f"http://{user}:{pwd}@{host}:{port}"

    # 3. Format: HOST:PORT:USER:PASS
    match2 = re.fullmatch(r"([a-zA-Z0-9\.\-]+):(\d+):(.+?):(.+)", proxy_raw)
    if match2:
        host, port, user, pwd = match2.groups()
        return f"http://{user}:{pwd}@{host}:{port}"

    return None

async def get_ip(proxy_url):
    try:
        transport = httpx.AsyncHTTPTransport(proxy=proxy_url)
        async with httpx.AsyncClient(transport=transport, timeout=10) as client:
            res = await client.get("https://ipinfo.io/json")
            if res.status_code == 200:
                return res.json().get("ip"), None
            return None, res.status_code
    except Exception as e:
        return None, str(e)

def get_proxy(user_id: int) -> str | None:
    if not os.path.exists(PROXY_FILE):
        return None
    try:
        data = json.load(open(PROXY_FILE))
        return data.get(str(user_id))
    except Exception:
        return None

@Client.on_message(filters.command("setpx") & filters.private)
async def set_proxy(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("<b>Format ❌:</b> `/setpx {proxy}`", quote=True)

    raw_proxy = message.text.split(maxsplit=1)[1].strip()
    proxy_url = normalize_proxy(raw_proxy)

    if not proxy_url:
        return await message.reply(
            "<pre>Invalid format ❌</pre>\n<b>Supported:</b>\n~ {ip}:{port}:{user}:{pass}\n~ {user}:{pass}@{ip}:{port}\n~ {protocol}://{user}:{pass}@{ip}:{port}",
            quote=True,
        )

    user_id = str(message.from_user.id)
    data = load_proxies()

    if data.get(user_id) == proxy_url:
        return await message.reply("<b>This proxy is already added ⚠️</b>", quote=True)

    msg = await message.reply("<pre>Validating Proxy 🔘</pre>", quote=True)

    ip1, err1 = await get_ip(proxy_url)
    await asyncio.sleep(2)
    ip2, err2 = await get_ip(proxy_url)

    if not ip1 or not ip2:
        err_msg = err1 or err2 or "Unknown error"
        return await msg.edit(f"<pre>Connection Failure ❌</pre>\n<b>~ Error :</b> <code>{err_msg}</code>")

    if ip1 == ip2:
        return await msg.edit(f"<pre>Proxy Risk ⚠️</pre>\n<b>Message :</b> <code>Provided Proxy Seems To be Risky</code>\n<b>Try Rotating|Residential Proxy</b>")

    # Save or Replace proxy for user
    data[user_id] = proxy_url
    save_proxies(data)

    await msg.edit(f"<pre>Proxy saved successfully! ✅</pre>")

@Client.on_message(filters.command("delpx") & filters.private)
async def delete_proxy(client, message: Message):
    user_id = str(message.from_user.id)
    data = load_proxies()

    if user_id not in data:
        return await message.reply("<b>No proxy was found to delete !!!</b>", quote=True)

    del data[user_id]
    save_proxies(data)
    await message.reply("<b>Your proxy has been removed ✅</b>", quote=True)

@Client.on_message(filters.command("getpx") & filters.private)
async def getpx_handler(client, message):
    user_id = message.from_user.id
    proxy = get_proxy(user_id)

    if not proxy:
        return await message.reply("<b>You haven't set any proxy yet ❌</b>")

    try:
        # Remove http:// if present
        proxy = proxy.replace("http://", "")
        creds, hostport = proxy.split("@")
        username = creds.split(":")[0]
        host = hostport.split(":")[0]

        await message.reply(
            f"<pre>Proxy | {user_id}\n"
            f"✦ <b>Username:</b> <code>{username}</code>\n"
            f"✦ <b>Host:</b> <code>{host}</code>"
        )
    except Exception as e:
        await message.reply(f"❌ Failed to parse proxy.\n<code>{e}</code>")


@Client.on_message(filters.command(["rproxy", "randproxy"]))
async def random_proxy_handler(client, message):
    """Get a random proxy from the proxy list"""
    if not PROXY_LIST:
        return await message.reply(
            "<pre>Proxy List Empty ❌</pre>\n<b>No proxies available in the database.</b>",
            quote=True
        )

    args = message.text.split()
    amount = 1
    if len(args) > 1 and args[1].isdigit():
        amount = min(int(args[1]), 10)  # Max 10 proxies at once

    user_name = message.from_user.first_name
    profile = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>"

    selected_proxies = random.sample(PROXY_LIST, min(amount, len(PROXY_LIST)))

    proxy_texts = []
    for px in selected_proxies:
        host = px.get("host", "N/A")
        port = px.get("port", "N/A")
        username = px.get("username", "N/A")
        password = px.get("password", "N/A")
        
        # Format: host:port:username:password
        proxy_str = f"{host}:{port}:{username}:{password}"
        proxy_texts.append(f"<code>{proxy_str}</code>")

    reply_text = f"""<pre>Random Proxy 🔄</pre>
━━━━━━━━━━━━━━━
<b>Amount:</b> <code>{len(selected_proxies)}</code>

""" + "\n".join(proxy_texts) + f"""
━━━━━━━━━━━━━━━
<b>Requested By:</b> {profile}"""

    await message.reply(reply_text, quote=True, disable_web_page_preview=True)


@Client.on_message(filters.command(["proxycount", "pxcount"]))
async def proxy_count_handler(client, message):
    """Get the total number of proxies available"""
    count = len(PROXY_LIST)
    await message.reply(
        f"<pre>Proxy Database 📊</pre>\n<b>Total Proxies:</b> <code>{count:,}</code>",
        quote=True
    )


@Client.on_message(filters.command(["fullproxy", "fpx"]))
async def full_proxy_format_handler(client, message):
    """Get a random proxy in full URL format"""
    if not PROXY_LIST:
        return await message.reply(
            "<pre>Proxy List Empty ❌</pre>\n<b>No proxies available in the database.</b>",
            quote=True
        )

    args = message.text.split()
    amount = 1
    if len(args) > 1 and args[1].isdigit():
        amount = min(int(args[1]), 10)  # Max 10 proxies at once

    user_name = message.from_user.first_name
    profile = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>"

    selected_proxies = random.sample(PROXY_LIST, min(amount, len(PROXY_LIST)))

    proxy_texts = []
    for px in selected_proxies:
        host = px.get("host", "N/A")
        port = px.get("port", "N/A")
        username = px.get("username", "N/A")
        password = px.get("password", "N/A")
        
        # Format: http://username:password@host:port
        proxy_str = f"http://{username}:{password}@{host}:{port}"
        proxy_texts.append(f"<code>{proxy_str}</code>")

    reply_text = f"""<pre>Full Proxy URL 🔗</pre>
━━━━━━━━━━━━━━━
<b>Amount:</b> <code>{len(selected_proxies)}</code>

""" + "\n".join(proxy_texts) + f"""
━━━━━━━━━━━━━━━
<b>Requested By:</b> {profile}"""

    await message.reply(reply_text, quote=True, disable_web_page_preview=True)