#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================
   قـويـره سوفت - QWAIRAH SOFT
   سكريبت ترحيل البيانات من الأنظمة القديمة
====================================================
"""

import sqlite3
import json
import os
import sys
from datetime import datetime

# ======================================
# الإعدادات
# ======================================
OLD_DB_PATH = "الحوش2025م.db"
NEW_DB_PATH = "qwairah_accounting.db"
LOG_FILE = f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"


def log(msg: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def create_new_schema(cursor):
    """إنشاء هيكل قاعدة البيانات الجديدة"""
    log("إنشاء هيكل قاعدة البيانات الجديدة...")

    cursor.executescript("""
        PRAGMA journal_mode=WAL;
        PRAGMA foreign_keys=ON;

        -- ====== الحسابات (4 مستويات) ======
        CREATE TABLE IF NOT EXISTS chart_of_accounts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT NOT NULL UNIQUE,
            name_ar     TEXT NOT NULL,
            name_en     TEXT,
            type        TEXT NOT NULL CHECK(type IN ('assets','liabilities_equity','expenses','revenue')),
            sub_type    TEXT,
            sub_sub_type TEXT,
            is_main     INTEGER DEFAULT 0,
            parent_code TEXT,
            phone       TEXT,
            address     TEXT,
            relatives   TEXT,
            opening_balance REAL DEFAULT 0,
            ceiling     REAL DEFAULT 0,
            enable_ceiling INTEGER DEFAULT 0,
            enable_whatsapp INTEGER DEFAULT 1,
            enable_sms  INTEGER DEFAULT 0,
            enable_telegram INTEGER DEFAULT 0,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== العملات ======
        CREATE TABLE IF NOT EXISTS currencies (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT NOT NULL UNIQUE,
            name_ar     TEXT NOT NULL,
            name_en     TEXT,
            exchange_rate REAL DEFAULT 1.0,
            is_base     INTEGER DEFAULT 0,
            symbol      TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== العملاء ======
        CREATE TABLE IF NOT EXISTS customers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name_ar     TEXT NOT NULL,
            name_en     TEXT,
            phone       TEXT,
            phone2      TEXT,
            address     TEXT,
            email       TEXT,
            tax_number  TEXT,
            account_code TEXT,
            credit_limit REAL DEFAULT 0,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== الموردون ======
        CREATE TABLE IF NOT EXISTS suppliers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name_ar     TEXT NOT NULL,
            name_en     TEXT,
            phone       TEXT,
            address     TEXT,
            email       TEXT,
            tax_number  TEXT,
            account_code TEXT,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== الأصناف ======
        CREATE TABLE IF NOT EXISTS items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name_ar     TEXT NOT NULL UNIQUE,
            name_en     TEXT,
            barcode     TEXT,
            unit        TEXT DEFAULT 'قطعة',
            category    TEXT DEFAULT 'عام',
            item_group  TEXT DEFAULT 'عام',
            sale_price  REAL DEFAULT 0,
            cost_price  REAL DEFAULT 0,
            stock       REAL DEFAULT 0,
            min_stock   REAL DEFAULT 0,
            max_stock   REAL DEFAULT 0,
            warehouse   TEXT DEFAULT 'المخزن الرئيسي',
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== المخازن ======
        CREATE TABLE IF NOT EXISTS warehouses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name_ar     TEXT NOT NULL UNIQUE,
            address     TEXT,
            manager     TEXT,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== فواتير المبيعات ======
        CREATE TABLE IF NOT EXISTS sales_invoices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no  INTEGER NOT NULL,
            date        TEXT NOT NULL,
            customer_id INTEGER REFERENCES customers(id),
            currency_id INTEGER REFERENCES currencies(id),
            exchange_rate REAL DEFAULT 1,
            payment_type TEXT DEFAULT 'آجل' CHECK(payment_type IN ('آجل','نقد')),
            invoice_type TEXT DEFAULT 'فاتورة' CHECK(invoice_type IN ('فاتورة','مرتجع')),
            warehouse   TEXT,
            subtotal    REAL DEFAULT 0,
            discount    REAL DEFAULT 0,
            other_fees  REAL DEFAULT 0,
            total       REAL DEFAULT 0,
            paid        REAL DEFAULT 0,
            remaining   REAL DEFAULT 0,
            paid_account TEXT,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sales_invoice_lines (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id  INTEGER NOT NULL REFERENCES sales_invoices(id) ON DELETE CASCADE,
            item_id     INTEGER REFERENCES items(id),
            item_name   TEXT,
            qty         REAL DEFAULT 1,
            price       REAL DEFAULT 0,
            total       REAL DEFAULT 0
        );

        -- ====== فواتير المشتريات ======
        CREATE TABLE IF NOT EXISTS purchase_invoices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no  INTEGER NOT NULL,
            date        TEXT NOT NULL,
            supplier_id INTEGER REFERENCES suppliers(id),
            currency_id INTEGER REFERENCES currencies(id),
            exchange_rate REAL DEFAULT 1,
            payment_type TEXT DEFAULT 'آجل',
            invoice_type TEXT DEFAULT 'فاتورة',
            warehouse   TEXT,
            subtotal    REAL DEFAULT 0,
            discount    REAL DEFAULT 0,
            other_fees  REAL DEFAULT 0,
            total       REAL DEFAULT 0,
            paid        REAL DEFAULT 0,
            remaining   REAL DEFAULT 0,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS purchase_invoice_lines (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id  INTEGER NOT NULL REFERENCES purchase_invoices(id) ON DELETE CASCADE,
            item_id     INTEGER REFERENCES items(id),
            item_name   TEXT,
            qty         REAL DEFAULT 1,
            price       REAL DEFAULT 0,
            total       REAL DEFAULT 0
        );

        -- ====== سندات القبض والصرف ======
        CREATE TABLE IF NOT EXISTS treasury_transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            voucher_no  INTEGER NOT NULL,
            type        TEXT NOT NULL CHECK(type IN ('receipt','payment')),
            date        TEXT NOT NULL,
            account_id  INTEGER REFERENCES chart_of_accounts(id),
            fund_account TEXT,
            currency_id INTEGER REFERENCES currencies(id),
            exchange_rate REAL DEFAULT 1,
            amount      REAL NOT NULL,
            description TEXT,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== القيود اليومية ======
        CREATE TABLE IF NOT EXISTS journal_entries (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_no    INTEGER NOT NULL,
            date        TEXT NOT NULL,
            description TEXT,
            currency_id INTEGER REFERENCES currencies(id),
            exchange_rate REAL DEFAULT 1,
            total_amount REAL DEFAULT 0,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS journal_entry_lines (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id    INTEGER NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
            account_id  INTEGER REFERENCES chart_of_accounts(id),
            account_name TEXT,
            debit       REAL DEFAULT 0,
            credit      REAL DEFAULT 0,
            description TEXT
        );

        -- ====== مصارفة العملات ======
        CREATE TABLE IF NOT EXISTS exchange_transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            exchange_no INTEGER NOT NULL,
            date        TEXT NOT NULL,
            from_account_id INTEGER REFERENCES chart_of_accounts(id),
            from_currency_id INTEGER REFERENCES currencies(id),
            to_account_id INTEGER REFERENCES chart_of_accounts(id),
            to_currency_id INTEGER REFERENCES currencies(id),
            from_amount REAL DEFAULT 0,
            to_amount   REAL DEFAULT 0,
            rate        REAL DEFAULT 1,
            description TEXT,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== عمليات المخزون ======
        CREATE TABLE IF NOT EXISTS inventory_operations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            op_no       INTEGER NOT NULL,
            type        TEXT NOT NULL CHECK(type IN ('import','export','transfer','adjustment','stocktake','add_warehouse')),
            date        TEXT NOT NULL,
            from_warehouse TEXT,
            to_warehouse TEXT,
            description TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS inventory_operation_lines (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            op_id       INTEGER NOT NULL REFERENCES inventory_operations(id) ON DELETE CASCADE,
            item_id     INTEGER REFERENCES items(id),
            item_name   TEXT,
            qty         REAL DEFAULT 0,
            price       REAL DEFAULT 0
        );

        -- ====== عروض الأسعار ======
        CREATE TABLE IF NOT EXISTS price_quotes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_no    INTEGER NOT NULL,
            date        TEXT NOT NULL,
            valid_days  INTEGER DEFAULT 7,
            customer_id INTEGER REFERENCES customers(id),
            currency_id INTEGER REFERENCES currencies(id),
            subtotal    REAL DEFAULT 0,
            discount    REAL DEFAULT 0,
            total       REAL DEFAULT 0,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== طلبات الشراء ======
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no    INTEGER NOT NULL,
            date        TEXT NOT NULL,
            expected_date TEXT,
            supplier_id INTEGER REFERENCES suppliers(id),
            currency_id INTEGER REFERENCES currencies(id),
            subtotal    REAL DEFAULT 0,
            discount    REAL DEFAULT 0,
            total       REAL DEFAULT 0,
            notes       TEXT,
            status      TEXT DEFAULT 'pending',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== المستخدمون والصلاحيات ======
        CREATE TABLE IF NOT EXISTS app_users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL UNIQUE,
            password    TEXT NOT NULL,
            is_admin    INTEGER DEFAULT 0,
            is_active   INTEGER DEFAULT 1,
            permissions TEXT DEFAULT '[]',
            allowed_accounts TEXT DEFAULT 'all',
            allowed_warehouses TEXT DEFAULT 'all',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== إعدادات النظام ======
        CREATE TABLE IF NOT EXISTS app_settings (
            key         TEXT PRIMARY KEY,
            value       TEXT,
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        -- ====== سجل العمليات ======
        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            action      TEXT NOT NULL,
            table_name  TEXT,
            record_id   INTEGER,
            details     TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );
    """)
    log("✅ تم إنشاء هيكل قاعدة البيانات")


def insert_defaults(cursor):
    """إدراج البيانات الافتراضية"""
    log("إدراج البيانات الافتراضية...")

    # عملة افتراضية
    cursor.execute("""
        INSERT OR IGNORE INTO currencies (code, name_ar, name_en, exchange_rate, is_base, symbol)
        VALUES ('SAR', 'ريال سعودي', 'Saudi Riyal', 1.0, 1, 'ر.س')
    """)

    # مخزن افتراضي
    cursor.execute("""
        INSERT OR IGNORE INTO warehouses (name_ar, address)
        VALUES ('المخزن الرئيسي', 'المقر الرئيسي')
    """)

    # مستخدم مدير
    cursor.execute("""
        INSERT OR IGNORE INTO app_users (username, password, is_admin, permissions)
        VALUES ('admin', '735162242', 1, '["all"]')
    """)

    # حسابات رئيسية افتراضية
    default_accounts = [
        ("1", "الأصول", None, "assets", None, None, 1),
        ("2", "التزامات وحقوق الملكية", None, "liabilities_equity", None, None, 1),
        ("3", "المصروفات", None, "expenses", None, None, 1),
        ("4", "الإيرادات", None, "revenue", None, None, 1),
        ("1-1", "أصول ثابتة", "1", "assets", "fixed", None, 1),
        ("1-2", "أصول متداولة", "1", "assets", "current", None, 1),
        ("1-2-1", "الصناديق", "1-2", "assets", "current", "cash", 1),
        ("1-2-1-1", "الصندوق الرئيسي", "1-2-1", "assets", "current", "cash", 0),
        ("1-2-2", "البنوك", "1-2", "assets", "current", "bank", 1),
        ("1-2-3", "العملاء", "1-2", "assets", "current", "customer", 1),
        ("1-2-4", "المخزون", "1-2", "assets", "current", "inventory", 1),
        ("2-1", "حقوق الملكية", "2", "liabilities_equity", "equity", None, 1),
        ("2-1-1", "رأس المال", "2-1", "liabilities_equity", "equity", "capital", 1),
        ("2-1-2", "الأرباح والخسائر", "2-1", "liabilities_equity", "equity", "profit", 1),
        ("2-1-3", "المسحوبات", "2-1", "liabilities_equity", "equity", "drawings", 1),
        ("2-2", "التزامات متداولة", "2", "liabilities_equity", "current_liabilities", None, 1),
        ("2-2-1", "الموردون", "2-2", "liabilities_equity", "current_liabilities", "supplier", 1),
        ("3-1", "تكاليف النشاط", "3", "expenses", "activity", None, 1),
        ("3-1-1", "المشتريات", "3-1", "expenses", "activity", "production", 1),
        ("3-1-1-1", "مشتريات نقدي", "3-1-1", "expenses", "activity", "production", 0),
        ("3-1-1-2", "مشتريات آجل", "3-1-1", "expenses", "activity", "production", 0),
        ("3-1-2", "مردودات المبيعات", "3-1", "expenses", "activity", "sale_returns", 1),
        ("3-1-3", "تكلفة المبيعات", "3-1", "expenses", "activity", "cost_sales", 0),
        ("3-1-4", "الخصم المسموح به", "3-1", "expenses", "activity", "discount_allowed", 0),
        ("3-1-5", "عجز وزيادة البضاعة", "3-1", "expenses", "activity", "inv_settle", 0),
        ("3-1-6", "البضاعة التالفة", "3-1", "expenses", "activity", "damaged", 0),
        ("3-2", "مصاريف تشغيلية وإدارية", "3", "expenses", "operational", None, 1),
        ("4-1", "إيرادات النشاط", "4", "revenue", "activity_rev", None, 1),
        ("4-1-1", "المبيعات", "4-1", "revenue", "activity_rev", "sales", 1),
        ("4-1-1-1", "مبيعات نقدي", "4-1-1", "revenue", "activity_rev", "sales", 0),
        ("4-1-1-2", "مبيعات آجل", "4-1-1", "revenue", "activity_rev", "sales", 0),
        ("4-1-2", "مردودات المشتريات", "4-1", "revenue", "activity_rev", "purch_returns", 1),
        ("4-1-3", "الخصم المكتسب", "4-1", "revenue", "activity_rev", "disc_earned", 0),
        ("4-1-4", "فوارق أسعار العملات", "4-1", "revenue", "other_rev", "fx_diff", 0),
        ("4-2", "إيرادات أخرى", "4", "revenue", "other_rev", None, 1),
    ]
    for acc in default_accounts:
        cursor.execute("""
            INSERT OR IGNORE INTO chart_of_accounts
            (code, name_ar, parent_code, type, sub_type, sub_sub_type, is_main)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, acc)

    log("✅ تم إدراج البيانات الافتراضية")


def migrate_from_old_db(old_path: str, new_cursor):
    """ترحيل البيانات من قاعدة البيانات القديمة"""
    if not os.path.exists(old_path):
        log(f"⚠️ الملف القديم غير موجود: {old_path}", "WARN")
        return 0

    log(f"🔄 فتح قاعدة البيانات القديمة: {old_path}")
    old_conn = sqlite3.connect(old_path)
    old_conn.row_factory = sqlite3.Row
    old_cursor = old_conn.cursor()

    total_migrated = 0

    # قائمة الجداول المحتملة في الأنظمة القديمة
    old_table_mappings = [
        # اسم الجدول القديم -> (جدول جديد, تعيين الأعمدة)
        ("accounts", "chart_of_accounts", {"name": "name_ar", "balance": "opening_balance"}),
        ("clients", "customers", {"name": "name_ar", "phone": "phone", "address": "address"}),
        ("suppliers", "suppliers", {"name": "name_ar", "phone": "phone"}),
        ("products", "items", {"name": "name_ar", "unit": "unit", "price": "sale_price", "cost": "cost_price", "qty": "stock"}),
        ("transactions", "journal_entries", {"date": "date", "details": "description", "amount": "total_amount"}),
    ]

    old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in old_cursor.fetchall()}
    log(f"📋 الجداول الموجودة في الملف القديم: {', '.join(existing_tables) if existing_tables else 'لا توجد جداول'}")

    for old_table, new_table, col_map in old_table_mappings:
        if old_table not in existing_tables:
            continue
        try:
            old_cursor.execute(f"SELECT * FROM {old_table}")
            rows = old_cursor.fetchall()
            count = 0
            for row in rows:
                row_dict = dict(row)
                new_row = {}
                for old_col, new_col in col_map.items():
                    if old_col in row_dict:
                        new_row[new_col] = row_dict[old_col]
                if new_row:
                    cols = ", ".join(new_row.keys())
                    placeholders = ", ".join(["?"] * len(new_row))
                    try:
                        new_cursor.execute(
                            f"INSERT OR IGNORE INTO {new_table} ({cols}) VALUES ({placeholders})",
                            list(new_row.values())
                        )
                        count += 1
                    except Exception as e:
                        log(f"  ⚠️ خطأ في الصف: {e}", "WARN")
            total_migrated += count
            log(f"  ✅ {old_table} → {new_table}: تم ترحيل {count} سجل")
        except Exception as e:
            log(f"  ❌ خطأ في الجدول {old_table}: {e}", "ERROR")

    old_conn.close()
    return total_migrated


def export_to_json(cursor, output_path: str):
    """تصدير البيانات إلى JSON للمراجعة"""
    log(f"📤 تصدير البيانات إلى {output_path}...")
    data = {}
    tables = ["chart_of_accounts", "currencies", "customers", "suppliers", "items",
              "sales_invoices", "purchase_invoices", "treasury_transactions", "journal_entries"]
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT 1000")
            cols = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
            data[table] = [dict(zip(cols, row)) for row in rows]
        except Exception:
            pass
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log(f"✅ تم التصدير إلى {output_path}")


def main():
    print("=" * 60)
    print("   قـويـره سوفت — QWAIRAH SOFT")
    print("   سكريبت ترحيل وإنشاء قاعدة البيانات")
    print("=" * 60)
    print()

    # إنشاء قاعدة البيانات الجديدة
    log(f"📂 إنشاء قاعدة البيانات: {NEW_DB_PATH}")
    new_conn = sqlite3.connect(NEW_DB_PATH)
    new_cursor = new_conn.cursor()

    try:
        create_new_schema(new_cursor)
        insert_defaults(new_cursor)

        # ترحيل من الملف القديم
        if len(sys.argv) > 1:
            old_db = sys.argv[1]
        else:
            old_db = OLD_DB_PATH

        if os.path.exists(old_db):
            log(f"\n🔄 بدء ترحيل البيانات من: {old_db}")
            count = migrate_from_old_db(old_db, new_cursor)
            log(f"✅ إجمالي السجلات المرحّلة: {count}")
        else:
            log(f"ℹ️ لم يتم العثور على ملف قديم ({old_db}) — تم إنشاء قاعدة بيانات جديدة نظيفة")

        new_conn.commit()

        # حفظ إحصاءات
        new_cursor.execute("SELECT COUNT(*) FROM chart_of_accounts")
        accs = new_cursor.fetchone()[0]
        new_cursor.execute("SELECT COUNT(*) FROM currencies")
        curr = new_cursor.fetchone()[0]
        new_cursor.execute("SELECT COUNT(*) FROM app_users")
        usrs = new_cursor.fetchone()[0]

        print("\n" + "=" * 60)
        log(f"🎉 اكتملت العملية بنجاح!")
        log(f"📊 الإحصاءات:")
        log(f"   • الحسابات: {accs}")
        log(f"   • العملات: {curr}")
        log(f"   • المستخدمون: {usrs}")
        log(f"   • قاعدة البيانات: {NEW_DB_PATH}")
        log(f"   • سجل العمليات: {LOG_FILE}")
        print("=" * 60)
        print("\n✅ تم بنجاح! قاعدة البيانات جاهزة للاستخدام مع قـويـره سوفت")

    except Exception as e:
        log(f"❌ خطأ عام: {e}", "ERROR")
        new_conn.rollback()
        raise
    finally:
        new_conn.close()


if __name__ == "__main__":
    main()
