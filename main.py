# قـويــره سوفت - Qwairah Soft Accounting System
# Google Colab / Local Launcher Script
# Run this file to launch the app in your browser from Google Colab or locally

import os
import sys
import json
import webbrowser
import subprocess
import urllib.request
from pathlib import Path

APP_NAME = "قـويــره سوفت"
APP_VERSION = "2.0"

def check_node():
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_node_colab():
    print("جاري تثبيت Node.js في Google Colab...")
    os.system("!curl -fsSL https://deb.nodesource.com/setup_18.x | bash -")
    os.system("!apt-get install -y nodejs")

def build_app():
    app_dir = Path(__file__).parent / "artifacts" / "qwairah-soft"
    if not app_dir.exists():
        print(f"خطأ: مجلد التطبيق غير موجود: {app_dir}")
        return False
    print("جاري تثبيت الاعتماديات...")
    os.system(f"cd {app_dir} && npm install --legacy-peer-deps")
    print("جاري بناء التطبيق...")
    result = os.system(f"cd {app_dir} && npm run build")
    return result == 0

def serve_locally(port=5173):
    app_dir = Path(__file__).parent / "artifacts" / "qwairah-soft"
    dist_dir = app_dir / "dist"
    if dist_dir.exists():
        print(f"تشغيل التطبيق على المنفذ {port}...")
        os.system(f"cd {dist_dir} && python3 -m http.server {port}")
    else:
        print("جاري تشغيل خادم التطوير...")
        os.system(f"cd {app_dir} && npx vite --port {port} --host 0.0.0.0")

def run_in_colab():
    """Launch the app in Google Colab with ngrok tunnel"""
    try:
        from google.colab import output
        from google.colab.output import eval_js
        IN_COLAB = True
    except ImportError:
        IN_COLAB = False

    if not IN_COLAB:
        print("هذا الكود مخصص لـ Google Colab. للتشغيل المحلي استخدم: python3 main.py --local")
        return

    print(f"🚀 تشغيل {APP_NAME} في Google Colab...")

    # Try to use pyngrok for tunnel
    try:
        os.system("pip install pyngrok -q")
        from pyngrok import ngrok
        port = 5173
        public_url = ngrok.connect(port)
        print(f"✅ التطبيق متاح على: {public_url}")
        serve_locally(port)
    except Exception as e:
        print(f"تعذر إنشاء نفق: {e}")
        print("جرب فتح index.html مباشرة في المتصفح")

def open_standalone():
    """Open the standalone index.html file"""
    html_file = Path(__file__).parent / "index.html"
    if html_file.exists():
        print(f"فتح ملف {html_file}")
        webbrowser.open(f"file://{html_file.absolute()}")
    else:
        print("ملف index.html غير موجود. قم بتشغيل: python3 main.py --build أولاً")

def main():
    args = sys.argv[1:]

    print(f"""
╔══════════════════════════════════════╗
║      {APP_NAME}              ║
║      نظام المحاسبة المالي المتكامل   ║
║      الإصدار {APP_VERSION}                      ║
╚══════════════════════════════════════╝
""")

    if "--standalone" in args or "--offline" in args:
        print("تشغيل النسخة المستقلة (بدون إنترنت)...")
        open_standalone()
        return

    if "--build" in args:
        if not check_node():
            print("Node.js غير مثبت. جاري التثبيت...")
            install_node_colab()
        build_app()
        return

    if "--colab" in args:
        run_in_colab()
        return

    if "--local" in args:
        serve_locally()
        return

    # Default: open standalone HTML
    print("خيارات التشغيل:")
    print("  --standalone  فتح الملف المستقل (بدون إنترنت)")
    print("  --build       بناء التطبيق (يتطلب Node.js)")
    print("  --local       تشغيل خادم محلي")
    print("  --colab       تشغيل في Google Colab")
    print()
    print("تشغيل النسخة المستقلة افتراضياً...")
    open_standalone()

if __name__ == "__main__":
    main()
