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

def load_proxies():
    return json.load(open(PROXY_FILE)) if os.path.exists(PROXY_FILE) else {}

def save_proxies(data):
    with open(PROXY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_proxy_csv():
    """Load proxies from CSV file"""
    proxies = []
    if os.path.exists(PROXY_CSV_FILE):
        with open(PROXY_CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    host = row.get("host", "").strip()
                    port = row.get("port", "").strip()
                    username = row.get("username", "").strip()
                    password = row.get("password", "").strip()
                    if host and port:
                        if username and password:
                            proxy_url = f"http://{username}:{password}@{host}:{port}"
                        else:
                            proxy_url = f"http://{host}:{port}"
                        proxies.append(proxy_url)
                except Exception:
                    continue
    return proxies

def get_random_proxy_from_csv():
    """Get a random proxy from the CSV file"""
    proxies = load_proxy_csv()
    if proxies:
        return random.choice(proxies)
    return None

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
    """Get user's custom proxy or fallback to random from CSV"""
    # First check user's custom proxy
    if os.path.exists(PROXY_FILE):
        try:
            data = json.load(open(PROXY_FILE))
            user_proxy = data.get(str(user_id))
            if user_proxy:
                return user_proxy
        except Exception:
            pass
    
    # Fallback to random proxy from CSV
    return get_random_proxy_from_csv()

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
    data = load_proxies()
    proxy = data.get(str(user_id))

    if not proxy:
        return await message.reply("<b>You haven't set any custom proxy yet ❌</b>\n<code>System will use auto-rotating proxies for you.</code>")

    try:
        # Remove http:// if present
        proxy_display = proxy.replace("http://", "")
        creds, hostport = proxy_display.split("@")
        username = creds.split(":")[0]
        host = hostport.split(":")[0]

        await message.reply(
            f"<pre>Proxy | {user_id}</pre>\n"
            f"✦ <b>Username:</b> <code>{username}</code>\n"
            f"✦ <b>Host:</b> <code>{host}</code>"
        )
    except Exception as e:
        await message.reply(f"❌ Failed to parse proxy.\n<code>{e}</code>")


@Client.on_message(filters.command("randpx"))
async def random_proxy_handler(client, message):
    """Get a random proxy from the CSV pool"""
    proxy = get_random_proxy_from_csv()
    
    if not proxy:
        return await message.reply(
            "<pre>No Proxies Available ❌</pre>\n<b>Proxy pool is empty.</b>",
            reply_to_message_id=message.id
        )
    
    msg = await message.reply("<pre>Fetching Random Proxy... 🔄</pre>", quote=True)
    
    # Test the proxy
    ip, err = await get_ip(proxy)
    
    if ip:
        try:
            proxy_display = proxy.replace("http://", "")
            if "@" in proxy_display:
                creds, hostport = proxy_display.split("@")
                username = creds.split(":")[0][:8] + "***"
                host = hostport.split(":")[0]
            else:
                host = proxy_display.split(":")[0]
                username = "N/A"
            
            await msg.edit(
                f"<pre>Random Proxy ✅</pre>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"<b>[•] Host:</b> <code>{host}</code>\n"
                f"<b>[•] IP:</b> <code>{ip}</code>\n"
                f"<b>[•] Status:</b> <code>Working</code>\n"
                f"━━━━━━━━━━━━━━━"
            )
        except:
            await msg.edit(f"<pre>Random Proxy ✅</pre>\n<b>IP:</b> <code>{ip}</code>")
    else:
        await msg.edit(f"<pre>Proxy Test Failed ❌</pre>\n<b>Error:</b> <code>{err}</code>")


@Client.on_message(filters.command("pxstats"))
async def proxy_stats_handler(client, message):
    """Show proxy pool statistics"""
    proxies = load_proxy_csv()
    user_proxies = load_proxies()
    
    reply_text = f"""<pre>Proxy Statistics 📊</pre>
━━━━━━━━━━━━━━━
<b>[•] Pool Size:</b> <code>{len(proxies)}</code>
<b>[•] Custom Proxies:</b> <code>{len(user_proxies)}</code>
<b>[•] Status:</b> <code>{"Active ✅" if proxies else "Empty ❌"}</code>
━━━━━━━━━━━━━━━
<b>Commands:</b>
<code>/setpx</code> - Set custom proxy
<code>/delpx</code> - Delete custom proxy
<code>/getpx</code> - View your proxy
<code>/randpx</code> - Get random proxy
<code>/testpx</code> - Test a proxy
━━━━━━━━━━━━━━━"""
    
    await message.reply(reply_text, reply_to_message_id=message.id)


@Client.on_message(filters.command("testpx"))
async def test_proxy_handler(client, message):
    """Test a specific proxy"""
    if len(message.command) < 2:
        return await message.reply(
            "<pre>Test Proxy ❌</pre>\n<b>Usage:</b> <code>/testpx {proxy}</code>",
            reply_to_message_id=message.id
        )
    
    raw_proxy = message.text.split(maxsplit=1)[1].strip()
    proxy_url = normalize_proxy(raw_proxy)
    
    if not proxy_url:
        return await message.reply(
            "<pre>Invalid format ❌</pre>\n<b>Supported:</b>\n~ {ip}:{port}:{user}:{pass}\n~ {user}:{pass}@{ip}:{port}\n~ {protocol}://{user}:{pass}@{ip}:{port}",
            quote=True,
        )
    
    msg = await message.reply("<pre>Testing Proxy... 🔄</pre>", quote=True)
    
    ip1, err1 = await get_ip(proxy_url)
    await asyncio.sleep(1)
    ip2, err2 = await get_ip(proxy_url)
    
    if not ip1 and not ip2:
        err_msg = err1 or err2 or "Unknown error"
        return await msg.edit(f"<pre>Proxy Test Failed ❌</pre>\n<b>Error:</b> <code>{err_msg}</code>")
    
    if ip1 == ip2:
        await msg.edit(
            f"<pre>Proxy Test ⚠️</pre>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"<b>[•] IP:</b> <code>{ip1}</code>\n"
            f"<b>[•] Status:</b> <code>Working (Static)</code>\n"
            f"<b>[•] Type:</b> <code>Datacenter/Static</code>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"<b>Note:</b> Same IP detected. Consider using rotating proxy."
        )
    else:
        await msg.edit(
            f"<pre>Proxy Test ✅</pre>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"<b>[•] IP 1:</b> <code>{ip1}</code>\n"
            f"<b>[•] IP 2:</b> <code>{ip2}</code>\n"
            f"<b>[•] Status:</b> <code>Working (Rotating)</code>\n"
            f"<b>[•] Type:</b> <code>Residential/Rotating</code>\n"
            f"━━━━━━━━━━━━━━━"
        )