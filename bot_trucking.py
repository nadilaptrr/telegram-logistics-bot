import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Tahapan percakapan (States)
TANGGAL, FACTORY, MATERIAL, MODAL = range(4)

# 1. Perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚚 *Sistem Tracking CV Frananda Utama*\n\n"
        "Halo! Mari catat pengiriman dengan mudah.\n"
        "Ketik /tambah untuk mulai mencatat data baru, atau /rekap untuk melihat laporan.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# 2. Mulai proses input
async def mulai_tambah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 Masukkan **Tanggal** pengiriman (Contoh: 07/04/2026):", parse_mode="Markdown")
    return TGLL

# Ubah state mapping
TGLL, FCT, MAT, MDL = range(4)

async def input_tanggal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['tanggal'] = update.message.text
    await update.message.reply_text("🏭 Masukkan nama **Factory / Pabrik** tujuan (Contoh: PT Changshin):", parse_mode="Markdown")
    return FCT

async def input_factory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['factory'] = update.message.text
    await update.message.reply_text("📦 Masukkan jenis **Material** (Contoh: Rubber):", parse_mode="Markdown")
    return MAT

async def input_material(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['material'] = update.message.text
    await update.message.reply_text("💸 Masukkan **Harga Modal** (angka saja, contoh: 1200000):", parse_mode="Markdown")
    return MDL

async def input_modal_dan_simpan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        modal = float(update.message.text)
        
        # OTOMATISASI INVOICE: Misal markup otomatis Rp 250.000 atau sesuaikan formula bisnis
        # Kamu bisa ubah logika hitung invoice di sini
        invoice = modal + 200000 
        
        tanggal = context.user_data['tanggal']
        factory = context.user_data['factory']
        material = context.user_data['material']
        
        # Simpan ke file teks database lokal
        data_baris = f"{tanggal} | {factory} | {material} | Modal: Rp {modal:,.2f} | Invoice (Auto): Rp {invoice:,.2f}\n"
        with open("database_trucking.txt", "a", encoding="utf-8") as f:
            f.write(data_baris)
            
        keuntungan = invoice - modal
        
        respon = (
            "✅ *Data Berhasil Disimpan & Invoice Otomatis Dibuat!*\n"
            f"📅 Tanggal: {tanggal}\n"
            f"🏭 Factory: {factory}\n"
            f"📦 Material: {material}\n"
            f"💸 Harga Modal: Rp {modal:,.0f}\n"
            f"💰 Harga Invoice (Otomatis): Rp {invoice:,.0f}\n"
            f"📈 Potensi Profit: Rp {keuntungan:,.0f}"
        )
        await update.message.reply_text(respon, parse_mode="Markdown")
        
    except ValueError:
        await update.message.reply_text("❌ Harga modal harus berupa angka! Silakan ulangi dari /tambah.")
        
    return ConversationHandler.END

async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Proses dibatalkan.")
    return ConversationHandler.END

# 3. Perintah /rekap
async def rekap_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists("database_trucking.txt"):
        await update.message.reply_text("📭 Belum ada data pengiriman.")
        return
        
    with open("database_trucking.txt", "r", encoding="utf-8") as f:
        isi_file = f.read()
        
    if not isi_file.strip():
        await update.message.reply_text("📭 Database masih kosong.")
        return
        
    if len(isi_file) > 4000:
        isi_file = isi_file[-4000:]
        
    await update.message.reply_text(f"📊 *Rekap Data Tracking CV Frananda Utama:*\n\n{isi_file}", parse_mode="Markdown")

if __name__ == '__main__':
    TOKEN = "8735223393:AAGEH40XzffIj4Tb3IOMdu9LuCXfPkKBSEg" # Ganti token bot kamu di sini
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Conversation handler untuk alur interaktif langkah demi langkah
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('tambah', mulai_tambah)],
        states={
            TGLL: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_tanggal)],
            FCT: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_factory)],
            MAT: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_material)],
            MDL: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_modal_dan_simpan)],
        },
        fallbacks=[CommandHandler('batal', batal)]
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rekap", rekap_data))
    application.add_handler(conv_handler)
    
    print("🤖 Bot Trucking Interaktif Berjalan...")
    application.run_polling()