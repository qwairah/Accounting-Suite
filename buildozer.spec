[app]

# معلومات التطبيق
title = قـويـره سوفت
package.name = qwairahsoft
package.domain = com.qwairahsoft.accounting

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,html,css,js,ttf,woff,woff2,svg,ico,webp
source.include_patterns = assets/*,fonts/*,dist/*,build/*

# الإصدار
version = 1.0

# المتطلبات
requirements = python3==3.10.12,kivy==2.3.0,android,pyjnius,pillow,requests

# التوجيه والشاشة
orientation = portrait
fullscreen = 1

# صلاحيات Android
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,READ_CONTACTS,CAMERA,VIBRATE,SEND_SMS,RECEIVE_SMS,ACCESS_NETWORK_STATE

# إصدارات Android SDK
android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b
android.ndk_api = 24

# المعماريات المدعومة
android.archs = arm64-v8a, armeabi-v7a

# النسخ الاحتياطي
android.allow_backup = True

# شعار التطبيق
android.icon.filename = %(source.dir)s/icon.png

# شاشة البداية
android.presplash.filename = %(source.dir)s/presplash.png
android.presplash_color = #0a1f0f

# نوع الملف الناتج
android.release_artifact = apk

# إعدادات Gradle
android.gradle_dependencies = implementation 'androidx.webkit:webkit:1.6.1'

# إضافة WebView
android.add_jars =
android.add_aars =

# متغيرات البيئة
android.env_vars =

# ملفات إضافية داخل APK
android.add_src =

# p4a
p4a.branch = master
p4a.fork = kivy

[buildozer]
log_level = 2
warn_on_root = 1
