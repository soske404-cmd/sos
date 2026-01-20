import json
import random
import string
from datetime import datetime, timedelta
from pyrogram import Client, filters
from BOT.helper.start import USERS_FILE, load_users, save_users, load_owner_id
import asyncio

user_redeem_cooldowns = {}
REDEEM_DELAY_SECONDS = 90  # 1 minute 30 seconds
REDEEM_PLAN_NAME = "Redeem Code"
REDEEM_CREDIT_BONUS = 50
REDEEM_ANTISPAM = 10
REDEEM_BADGE = "🎁"
DEFAULT_BADGE = "🧿"
DEFAULT_ANTISPAM = 15
DEFAULT_MLIMIT = 5
EXPIRY_SECONDS = 86400  # 1 day

OWNER_ID = load_owner_id()
REDEEM_FILE = "DATA/redeems.json"

def load_redeems():
    try:
        with open(REDEEM_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_redeems(data):
    with open(REDEEM_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_redeem_code(length=8):
    """Generates a random redeem code consisting of uppercase letters and numbers."""
    characters = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(characters) for _ in range(length))
    return code

@Client.on_message(filters.command("red") & ~filters.edited)
async def generate_redeem(client, message):
    if str(message.from_user.id) != OWNER_ID:
        return await message.reply_text(
            "❌ You don't have permission to generate redeem codes.",
            reply_to_message_id=message.id
        )
    
    try:
        amount = int(message.command[1])
        credits = int(message.command[2]) if len(message.command) > 2 else 50
    except:
        return await message.reply_text(
            "<pre>Usage ❌</pre>\n"
            "<b>Format:</b> <code>/red {amount} {credits}</code>\n"
            "<b>Example:</b> <code>/red 5 100</code>\n"
            "<b>~ Generates 5 codes of 100 credits each</b>",
            reply_to_message_id=message.id
        )
    
    redeems = load_redeems()
    codes = []

    for _ in range(amount):
        while True:
            redeem_code = "Sos-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            if redeem_code not in redeems:
                break

        redeems[redeem_code] = {
            "used": False,
            "used_by": None,
            "used_at": None,
            "credits": credits
        }
        codes.append(redeem_code)

    save_redeems(redeems)

    msg = f"<pre>[✦] Redeem Generated ✅</pre>\n"
    msg += f"<b>[ϟ] Amount :</b> <code>{amount}</code>\n"
    msg += f"<b>[ϟ] Credits :</b> <code>{credits}</code>\n"
    msg += "━━━━━━━━━━━━━\n"
    for code in codes:
        msg += f"<b>Code :</b> <code>{code}</code>\n"
        msg += f"<b>Value :</b> <code>{credits} Credits</code>\n"
        msg += "━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
    msg += "<pre>Use /redeem Sos-XXXXXXXXXXXX to Redeem</pre>"

    await message.reply_text(msg, reply_to_message_id=message.id)

@Client.on_message(filters.command("redeem") & ~filters.edited)
async def redeem_code(client, message):
    users = load_users()
    redeems = load_redeems()
    user_id = str(message.from_user.id)

    if len(message.command) < 2:
        return await message.reply_text("Usage: /redeem <code>", reply_to_message_id=message.id)

    code = message.command[1]
    
    if code not in redeems:
        return await message.reply_text(
            f"<b>Redeemed Failed ⚠️</b>\n<pre>• Code : {code}\n• Message : Provided Code Is Wrong</pre>\n<code>Please Provide Correct Code</code>",
            reply_to_message_id=message.id
        )
    
    if redeems[code]["used"]:
        return await message.reply_text(
            f"<b>Redeemed Failed ⚠️</b>\n<pre>• Code : {code}\n• Message : Code Is Redeemed By Another Users</pre>\n<code>Please Try Different Code</code>",
            reply_to_message_id=message.id
        )

    if user_id == OWNER_ID:
        return await message.reply_text("😄 You're the owner, you don’t need to redeem codes.", reply_to_message_id=message.id)

    if user_id not in users:
        return await message.reply_text("❌ Please register first using /start or /register", reply_to_message_id=message.id)

    # Get credits from the code (or use default 50)
    code_credits = redeems[code].get("credits", REDEEM_CREDIT_BONUS)

    user = users[user_id]
    plan = user.get("plan", {})
    current_credits = plan.get("credits", 0)

    if current_credits != "∞":
        try:
            current_credits = int(current_credits)
            new_credits = current_credits + code_credits
        except:
            new_credits = code_credits
    else:
        new_credits = "∞"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    expires_at = (datetime.now() + timedelta(seconds=EXPIRY_SECONDS)).strftime("%Y-%m-%d %H:%M:%S")

    current_plan = plan.get("plan", "Free")
    if current_plan == "Free":
        user["plan"].update({
            "plan": REDEEM_PLAN_NAME,
            "credits": new_credits,
            "badge": REDEEM_BADGE,
            "antispam": REDEEM_ANTISPAM,
            "activated_at": now,
            "expires_at": expires_at
        })
        user["role"] = REDEEM_PLAN_NAME
    elif current_plan in ["Plus", "Pro", "Elite", "VIP", "ULTIMATE"]:
        # User already has a paid plan — just increase credits
        user["plan"]["credits"] = new_credits
        # Don't change anything else!
    else:
        # Any unknown or future plan, just update credits and expire only if no custom plan logic exists
        user["plan"]["credits"] = new_credits
        user["plan"]["antispam"] = REDEEM_ANTISPAM
        user["plan"]["expires_at"] = expires_at

    user["plan"]["keyredeem"] = user["plan"].get("keyredeem", 0) + 1

    redeems[code]["used"] = True
    redeems[code]["used_by"] = user_id
    redeems[code]["used_at"] = now

    save_users(users)
    save_redeems(redeems)

    await message.reply_text(
        f"<b>Redeemed Successfully ✅</b>\n<pre>• Code : {code}\n• ID : {user_id}</pre>\n"
        f"<code>{code_credits} Credits are added to your account</code>\n"
        f"<code>Antispam Reduced To 10s For One Day!</code>",
        reply_to_message_id=message.id
    )

async def check_and_expire_redeem_plans(app: Client):
    while True:
        users = load_users()
        now = datetime.now()
        changed = False

        for user_id, user in users.items():
            plan = user.get("plan", {})
            if plan.get("plan") == REDEEM_PLAN_NAME and plan.get("expires_at"):
                try:
                    expiry_time = datetime.strptime(plan["expires_at"], "%Y-%m-%d %H:%M:%S")
                    if now >= expiry_time:
                        # Revert to Free plan
                        user["plan"].update({
                            "plan": "Free",
                            "activated_at": user.get("registered_at", plan.get("activated_at", now.strftime("%Y-%m-%d %H:%M:%S"))),
                            "expires_at": None,
                            "antispam": DEFAULT_ANTISPAM,
                            "mlimit": DEFAULT_MLIMIT,
                            "badge": DEFAULT_BADGE
                        })
                        user["role"] = "Free"
                        changed = True

                        # Notify user
                        try:
                            await app.send_message(
                                int(user_id),
                                "<b>🎁 Your redeem plan has expired.</b>\nYou are now on Free plan again."
                            )
                        except:
                            pass

                        # Notify owner
                        try:
                            await app.send_message(
                                OWNER_ID,
                                f"ℹ️ Redeem plan for <code>{user_id}</code> has expired and reverted to Free."
                            )
                        except:
                            pass
                except Exception as e:
                    print(f"[Redeem Expiry Error] {user_id}: {e}")

        if changed:
            save_users(users)

        await asyncio.sleep(10)
