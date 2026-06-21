# ربات تلگرام مدیکال

ربات جزوه/مشاوره‌ی تلگرام. **هیچ دیتابیسی داخل خودش ندارد** — همه‌ی داده‌ها از طریق
API پروژه‌ی `medical_website` (بک‌اند Django) روی HTTPS خوانده/نوشته می‌شود. این ربات
برای اجرا روی یک **سرور جدا** طراحی شده و فقط به API سایت وصل می‌شود.

```
ربات (سرور جدا)  ──HTTPS + X-Bot-Key──▶  API سایت (/api/tgbot/...)  ──▶  Postgres
   TOKEN/API_ID داخل .env خودش                       پنل سایت همین داده‌ها را مدیریت می‌کند
```

فایل‌های جزوه از **دانلود سنتر** سایت می‌آیند: در پنل، تب «ربات تلگرام → فایل‌ها» تیک
«نمایش در ربات» را بزنید تا فایل در ربات دیده شود.

---

## ۱) پیش‌نیازها
- یک سرور با Docker
- توکن ربات از [@BotFather](https://t.me/BotFather)
- `API_ID` و `API_HASH` از <https://my.telegram.org>
- آدرس API سایت و یک `API_KEY` مشترک

## ۲) تنظیم بک‌اند سایت (یک‌بار)
کلید مشترک را روی بک‌اند ست کنید (یکی از دو روش):
- متغیر محیطی: `TGBOT_API_KEY=<یک رشتهٔ تصادفی قوی>`
- یا از پنل، یک SiteSetting با کلید `tgbot_api_key` و همان مقدار

> تا وقتی `API_KEY` دو طرف یکی نباشد، بک‌اند درخواست ربات را با `403` رد می‌کند.

اگر اپ `tgbot` تازه دیپلوی شده، یادتان باشد `migrate` اجرا شود (در `update.sh` خودکار است).

## ۳) تنظیم `.env` ربات
فایل `robot_telegram/.env`:
```ini
TOKEN=123456:ABC...            # توکن ربات
API_ID=1234567                 # از my.telegram.org
API_HASH=abcdef0123...         # از my.telegram.org

API_BASE_URL=https://apiwebsite.medicalstus.ir/api
API_KEY=<همان کلیدی که روی بک‌اند گذاشتید>

# پروکسی (اختیاری) | 0 یا 1
PROXY=0
PROXY_ADDR="127.0.0.1"
PROXY_PORT="10808"
```

## ۴) ساخت و اجرا (فقط Docker — بدون docker-compose)
```bash
cd robot_telegram
docker build -t medical-bot .

docker run -d --name medical-bot --restart unless-stopped \
  --env-file .env \
  -v "$PWD/session:/app/session" \
  medical-bot
```
- `--restart unless-stopped` → اگر کرش کرد خودکار بالا می‌آید (جای supervisorِ `start.py`).
- `-v session:/app/session` → فایل session پایرگرام حفظ می‌شود تا هر restart دوباره لاگین نکند.

### لاگ‌ها / به‌روزرسانی
```bash
docker logs -f medical-bot
docker rm -f medical-bot && docker build -t medical-bot . && docker run -d ...   # آپدیت
```

---

## ساختار
| مسیر | توضیح |
|---|---|
| `bot.py` | راه‌اندازی کلاینت و ثبت هندلرها |
| `utils/api.py` | کلاینت HTTP به API سایت (جایگزین MySQL) |
| `utils/env.py` | خواندن `.env` |
| `handlers/users/` | منوی کاربر (جزوه‌ها، مشاوران، قبولی‌ها، رضایت‌ها) |
| `handlers/admins/` | پنل مدیریت داخل ربات (ادمین‌ها، کانال‌ها، پیام‌ها) |

## مدیریت از پنل سایت
بخش **«ربات تلگرام»** در پنل ادمین: آمار، متن دکمه‌ها و پیام‌ها، کاربران، ادمین‌ها،
کانال‌های عضویت اجباری، و انتخاب فایل‌های دانلود سنتر برای نمایش در ربات.
