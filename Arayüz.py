import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import requests
from datetime import datetime
import json
import os
import string
import re 

DOSYA_ADI = "kullanicilar.json"

if not os.path.exists(DOSYA_ADI):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump({}, f)

try:
    with open(DOSYA_ADI, "r", encoding="utf-8") as f:
        icerik = f.read().strip()
        if icerik:
            kullanicilar = json.loads(icerik)
        else:
            kullanicilar = {}
except Exception as e:
    print("JSON dosyası yüklenemedi:", e)
    kullanicilar = {}

def kaydet():
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(kullanicilar, f, ensure_ascii=False, indent=4)

#------------------------------DÖVİZ İŞLEMMLERİ-------------------------------------------   
#      
def doviz_penceresi(kullanici, refresh=None):
    pencere = tk.Toplevel()
    pencere.title("Döviz İşlemleri")
    pencere.geometry("300x350")
    pencere.configure(bg="#E3F2FD")
    pencere.iconbitmap(r"C:\Users\ardaa\Desktop\ADVANCED PHYTON PROJESİ\b_abc_bank_logo.ico")
  

    tk.Label(pencere, text="Baz Para:", font=("Segoe UI", 11, "bold"), bg="#E3F2FD").pack()
    baz_var = tk.StringVar(value="TRY")

    optionmenu_baz = tk.OptionMenu(pencere, baz_var, "TRY", "USD", "EUR")
    optionmenu_baz.config(
        bg="#E3F2FD",
        fg="#0D47A1",
        font=("Segoe UI", 10, "bold"),
        activebackground="#BBDEFB",
        highlightthickness=0
    )
    optionmenu_baz["menu"].config(
        bg="#E3F2FD",
        fg="#0D47A1",
        font=("Segoe UI", 10)
    )
    optionmenu_baz.pack(pady=5)

    
    tk.Label(pencere, text="Hedef Para:", font=("Segoe UI", 11, "bold"), bg="#E3F2FD").pack()
    hedef_var = tk.StringVar(value="USD")

    optionmenu_hedef = tk.OptionMenu(pencere, hedef_var, "TRY", "USD", "EUR")
    optionmenu_hedef.config(
        bg="#E3F2FD",
        fg="#0D47A1",
        font=("Segoe UI", 10, "bold"),
        activebackground="#BBDEFB",
        highlightthickness=0
    )
    optionmenu_hedef["menu"].config(
        bg="#E3F2FD",
        fg="#0D47A1",
        font=("Segoe UI", 10)
    )
    optionmenu_hedef.pack(pady=5)

    
    tk.Label(pencere, text="Dönüştürülecek Miktar:", font=("Segoe UI", 11, "bold"), bg="#E3F2FD").pack()
    entry_miktar = tk.Entry(pencere)
    entry_miktar.pack()

    
    def donustur():
        baz = baz_var.get()
        hedef = hedef_var.get()
        try:
            miktar = float(entry_miktar.get())
            if miktar <= 0:
                messagebox.showerror("Hata", "Lütfen pozitif bir miktar girin.")
                return
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin.")
            return

        if baz == hedef:
            messagebox.showinfo("Bilgi", "Aynı para birimi seçildi.")
            return

        mevcut_bakiye = kullanicilar[kullanici]["bakiye"].get(baz, 0.0)
        if miktar > mevcut_bakiye:
            messagebox.showerror("Hata", f"{baz} bakiyesi yetersiz.")
            return

        
        cevap = messagebox.askyesno(
            "Onay",
            f"{miktar:.2f} {baz} → {hedef} dönüştürmek istiyor musunuz?")
        
        if not cevap:
            return

        try:
            response = requests.get(f"https://api.frankfurter.app/latest?amount={miktar}&from={baz}&to={hedef}")
            response.raise_for_status()
            data = response.json()
            yeni_miktar = data["rates"][hedef]

            kullanicilar[kullanici]["bakiye"][baz] -= miktar
            kullanicilar[kullanici]["bakiye"][hedef] = kullanicilar[kullanici]["bakiye"].get(hedef, 0.0) + yeni_miktar

            zaman = datetime.now().strftime("%d.%m.%Y %H:%M")
            kayit = f"{zaman} - Döviz: {miktar:.2f} {baz} → {yeni_miktar:.2f} {hedef} dönüştürüldü."
            kullanicilar[kullanici]["gecmis"].insert(0, kayit)
            kullanicilar[kullanici]["gecmis"] = kullanicilar[kullanici]["gecmis"][:20]

            kaydet()
            messagebox.showinfo("Başarılı", kayit)
            if refresh:
                refresh()

        except Exception as e:
            messagebox.showerror("Hata", f"Döviz bilgisi alınamadı.\n\n{e}")

    
    tk.Button(pencere, text="Dönüştür", font=("Segoe UI", 10, "bold"), width=15,
              fg="white", bg="#1565C0", command=donustur).pack(pady=10)

    tk.Button(pencere, text="Kapat", font=("Segoe UI", 10, "bold"), width=15,
              fg="white", bg="#D32F2F", command=pencere.destroy).pack(pady=5)
    
#----------------------------------GEÇMİŞ İŞLEMLER---------------------------------

def gecmis_penceresi(kullanici):
    pencere = tk.Toplevel()
    pencere.title("Geçmiş İşlemler")
    pencere.geometry("500x400")
    pencere.configure(bg="#E3F2FD")
    pencere.iconbitmap(r"C:\Users\ardaa\Desktop\ADVANCED PHYTON PROJESİ\b_abc_bank_logo.ico")
 

    tk.Label(pencere, text="Geçmiş İşlemler", font=("Segoe UI", 15, "bold"), bg="#E3F2FD").pack(pady=10)

    text_gecmis = tk.Text(pencere, wrap="word", height=15, width=60, bg="#E3F2FD", font=("Segoe UI", 10, "bold"))
    text_gecmis.pack(padx=10, pady=5)
    text_gecmis.config(state=tk.NORMAL)
    text_gecmis.delete("1.0", tk.END)


    text_gecmis.tag_configure("bold", font=("Segoe UI", 10, "bold"))

    gecmis_listesi = kullanicilar.get(kullanici, {}).get("gecmis", [])
    if not gecmis_listesi:
        text_gecmis.insert(tk.END, "Herhangi bir işlem geçmişi bulunamadı.")
    else:
        for kayit in gecmis_listesi[:20]:
            start_index = text_gecmis.index(tk.END)
            text_gecmis.insert(tk.END, kayit + "\n\n")
            end_index = text_gecmis.index(tk.END)
            text_gecmis.tag_add("bold", start_index, end_index)

    text_gecmis.config(state=tk.DISABLED)

    def gecmisi_temizle():
        cevap = messagebox.askyesno("Onay", "Tüm işlem geçmişini silmek istediğinize emin misiniz?")
        if cevap:
            kullanicilar[kullanici]["gecmis"] = []
            kaydet()
            text_gecmis.config(state=tk.NORMAL)
            text_gecmis.delete("1.0", tk.END)
            text_gecmis.insert(tk.END, "Geçmiş başarıyla silindi.")
            text_gecmis.config(state=tk.DISABLED)
            messagebox.showinfo("Başarılı", "İşlem geçmişi başarıyla silindi.")

    buton_stil = {"font": ("Segoe UI", 10, "bold")}

    tk.Button(pencere, text="Geçmişi Sil", command=gecmisi_temizle, width=15, fg="white", bg="#1565C0", **buton_stil).pack(pady=5)
    tk.Button(pencere, text="Kapat", command=pencere.destroy, width=15, fg="white", bg="#D32F2F", **buton_stil).pack(pady=5)

#----------------------------------------PARA İŞLEMLERİ----------------------------------------------

def para_penceresi(kullanici, refresh=None):
    pencere = tk.Toplevel()
    pencere.title("Para İşlemleri")
    pencere.geometry("300x350")
    pencere.config(bg="#E3F2FD")
    pencere.iconbitmap(r"C:\Users\ardaa\Desktop\ADVANCED PHYTON PROJESİ\b_abc_bank_logo.ico")

    tk.Label(pencere, text="İşlem Türü:", font=("Segoe UI", 11, "bold"), bg="#E3F2FD").pack()
    islem_tipi_var = tk.StringVar(value="Yatırma")

    optionmenu_islem = tk.OptionMenu(pencere, islem_tipi_var, "Yatırma", "Çekme")
    optionmenu_islem.config(
        bg="#E3F2FD",
        fg="#0D47A1",
        font=("Segoe UI", 10, "bold"),
        activebackground="#BBDEFB",
        highlightthickness=0)

    optionmenu_islem["menu"].config(
        bg="#E3F2FD",
        fg="#0D47A1",
        font=("Segoe UI", 10))
    
    optionmenu_islem.pack(pady=5)

    
    tk.Label(pencere, text="Para Birimi:", font=("Segoe UI", 11, "bold"), bg="#E3F2FD").pack()
    para_birimi_var = tk.StringVar(value="TRY")

    optionmenu_para = tk.OptionMenu(pencere, para_birimi_var, "TRY", "USD", "EUR")
    optionmenu_para.config(
        bg="#E3F2FD",
        fg="#0D47A1",
        font=("Segoe UI", 10, "bold"),
        activebackground="#BBDEFB",
        highlightthickness=0)

    optionmenu_para["menu"].config(
        bg="#E3F2FD",
        fg="#0D47A1",
        font=("Segoe UI", 10))

    optionmenu_para.pack(pady=5)

    
    tk.Label(pencere, text="Miktar:", font=("Segoe UI", 11, "bold"), bg="#E3F2FD").pack()
    entry_miktar = tk.Entry(pencere)
    entry_miktar.pack()

    
    def islem_yap():
        islem_tipi = islem_tipi_var.get()
        para_birimi = para_birimi_var.get()
        try:
            miktar = float(entry_miktar.get())
            if miktar <= 0:
                messagebox.showerror("Hata", "Lütfen pozitif bir miktar girin.")
                return
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin.")
            return

        bakiye_data = kullanicilar[kullanici].get("bakiye", {})
        if not isinstance(bakiye_data, dict):
            bakiye_data = {"TRY": float(bakiye_data)}

        kullanicilar[kullanici]["bakiye"] = bakiye_data
        bakiye = bakiye_data.get(para_birimi, 0.0)

        onay = messagebox.askyesno("Onay", f"{miktar:.2f} {para_birimi} için {islem_tipi} işlemini yapmak istediğinize emin misiniz?")
        if not onay:
            return

        if islem_tipi == "Çekme":
            if miktar > bakiye:
                messagebox.showerror("Hata", f"{para_birimi} bakiyeniz yetersiz.")
                return
            kullanicilar[kullanici]["bakiye"][para_birimi] -= miktar
        else:
            kullanicilar[kullanici]["bakiye"][para_birimi] = bakiye + miktar

        zaman = datetime.now().strftime("%d.%m.%Y %H:%M")
        kayit = f"{zaman} - Para {islem_tipi.lower()} işlemi: {miktar:.2f} {para_birimi}."
        kullanicilar[kullanici]["gecmis"].insert(0, kayit)
        kullanicilar[kullanici]["gecmis"] = kullanicilar[kullanici]["gecmis"][:20]

        kaydet()
        messagebox.showinfo("Başarılı", kayit)
        if refresh:
            refresh()
        pencere.destroy()

    
    tk.Button(pencere, text="İşlemi Gerçekleştir", font=("Segoe UI", 10, "bold"), width=18,
              bg="#1565C0", fg="white", command=islem_yap).pack(pady=15)
    tk.Button(pencere, text="Kapat", font=("Segoe UI", 10, "bold"), width=18,
              fg="white", bg="#D32F2F", command=pencere.destroy).pack()


#--------------------------------HAVALE EKRANI-------------------------------------
def havale_penceresi(gonderen_kullanici, refresh=None):
    pencere = tk.Toplevel()
    pencere.title("Havale İşlemleri")
    pencere.geometry("450x400")
    pencere.config(bg="#E3F2FD")
    pencere.iconbitmap(r"C:\Users\ardaa\Desktop\ADVANCED PHYTON PROJESİ\b_abc_bank_logo.ico")


    tk.Label(pencere, text="Alıcı Kullanıcı ID:", font=("Segoe UI", 10, "bold"), bg="#E3F2FD").pack()
    entry_alici_id = tk.Entry(pencere)
    entry_alici_id.pack()


    tk.Label(pencere, text="Alıcı İsmi:", font=("Segoe UI", 10, "bold"), bg="#E3F2FD").pack()
    entry_alici_isim = tk.Entry(pencere)
    entry_alici_isim.pack()


    tk.Label(pencere, text="Alıcı Soyismi:", font=("Segoe UI", 10, "bold"), bg="#E3F2FD").pack()
    entry_alici_soyisim = tk.Entry(pencere)
    entry_alici_soyisim.pack()


    tk.Label(pencere, text="Para Birimi:", font=("Segoe UI", 10, "bold"), bg="#E3F2FD").pack()
    para_birimi_var = tk.StringVar(value="TRY")

    optionmenu_para = tk.OptionMenu(pencere, para_birimi_var, "TRY", "USD", "EUR")
    optionmenu_para.config(
        bg="#E3F2FD",
        fg="#0D47A1",
        font=("Segoe UI", 10, "bold"),
        activebackground="#BBDEFB",
        highlightthickness=0)
    
    optionmenu_para["menu"].config(
        bg="#E3F2FD",
        fg="#0D47A1",
        font=("Segoe UI", 10))
    
    optionmenu_para.pack(pady=5)

    
    tk.Label(pencere, text="Gönderilecek Miktar:", font=("Segoe UI", 10, "bold"), bg="#E3F2FD").pack()
    entry_miktar = tk.Entry(pencere)
    entry_miktar.pack()

    def havale_yap():
        alici_id = entry_alici_id.get().strip()
        para_birimi = para_birimi_var.get()
        try:
            miktar = float(entry_miktar.get())
            if miktar <= 0:
                messagebox.showerror("Hata", "Lütfen geçerli bir miktar girin.")
                return
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin.")
            return

        if alici_id not in kullanicilar:
            messagebox.showerror("Hata", "Alıcı bulunamadı.")
            return

        kullanici_bakiye = kullanicilar[gonderen_kullanici]["bakiye"].get(para_birimi, 0.0)
        if miktar > kullanici_bakiye:
            messagebox.showerror("Hata", f"{para_birimi} bakiyeniz yetersiz.")
            return

        onay = messagebox.askyesno("Onay", f"{miktar:.2f} {para_birimi} göndermek istediğinize emin misiniz?")
        if not onay:
            return

        
        kullanicilar[gonderen_kullanici]["bakiye"][para_birimi] -= miktar
        kullanicilar[alici_id]["bakiye"][para_birimi] = kullanicilar[alici_id]["bakiye"].get(para_birimi, 0.0) + miktar

        zaman = datetime.now().strftime("%d.%m.%Y %H:%M")
        kayit_gonderen = f"{zaman} - Havale: {miktar:.2f} {para_birimi} {alici_id} ID'li kullanıcıya gönderildi."
        kayit_alici = f"{zaman} - Havale: {miktar:.2f} {para_birimi} {gonderen_kullanici} ID'li kullanıcıdan alındı."

        kullanicilar[gonderen_kullanici]["gecmis"].insert(0, kayit_gonderen)
        kullanicilar[gonderen_kullanici]["gecmis"] = kullanicilar[gonderen_kullanici]["gecmis"][:20]

        kullanicilar[alici_id]["gecmis"].insert(0, kayit_alici)
        kullanicilar[alici_id]["gecmis"] = kullanicilar[alici_id]["gecmis"][:20]

        kaydet()
        messagebox.showinfo("Başarılı", kayit_gonderen)
        if refresh:
            refresh()
        pencere.destroy()

    
    tk.Button(pencere, text="Gönder", font=("Segoe UI", 10, "bold"), width=15, fg="white", bg="#1565C0", command=havale_yap).pack(pady=10)
    tk.Button(pencere, text="İptal", font=("Segoe UI", 10, "bold"), width=15, fg="white", bg="#D32F2F", command=pencere.destroy).pack(pady=5)


# -------------------------------HESAP OLUŞTURMA EKRANI------------------------------------
def hesap_olustur():
    pencere = tk.Toplevel()
    pencere.title("Hesap Oluştur")
    pencere.geometry("450x500")
    pencere.configure(bg="#E3F2FD")
    pencere.iconbitmap(r"C:\Users\ardaa\Desktop\ADVANCED PHYTON PROJESİ\b_abc_bank_logo.ico")


    tk.Label(pencere, text="Kullanıcı ID:", bg="#E3F2FD", font=("Segoe UI", 10, "bold")).pack()
    entry_kullanici = tk.Entry(pencere)
    entry_kullanici.pack()

    tk.Label(pencere, text="İsim:", bg="#E3F2FD", font=("Segoe UI", 10, "bold")).pack()
    entry_isim = tk.Entry(pencere)
    entry_isim.pack()

    tk.Label(pencere, text="Soyisim:", bg="#E3F2FD", font=("Segoe UI", 10, "bold")).pack()
    entry_soyisim = tk.Entry(pencere)
    entry_soyisim.pack()

    tk.Label(pencere, text="Kart Numarası (16 haneli):", bg="#E3F2FD", font=("Segoe UI", 10, "bold")).pack()
    entry_kart_no = tk.Entry(pencere)
    entry_kart_no.pack()

    tk.Label(pencere, text="Son Geçerlilik Tarihi (MM/YY):", bg="#E3F2FD", font=("Segoe UI", 10, "bold")).pack()
    entry_son_gecerlilik = tk.Entry(pencere)
    entry_son_gecerlilik.pack()

    tk.Label(pencere, text="Güvenlik Kodu (3 haneli):", bg="#E3F2FD", font=("Segoe UI", 10, "bold")).pack()
    entry_guvenlik_kodu = tk.Entry(pencere)
    entry_guvenlik_kodu.pack()

    tk.Label(pencere, text="Şifre:", bg="#E3F2FD", font=("Segoe UI", 10, "bold")).pack()
    entry_sifre = tk.Entry(pencere, show="*")
    entry_sifre.pack()

    def sifre_goster_gizle():
        if sifre_var.get():
            entry_sifre.config(show="")
        else:
            entry_sifre.config(show="*")

    sifre_var = tk.BooleanVar()
    tk.Checkbutton(pencere, text="Şifreyi Göster", bg="#E3F2FD", font=("Segoe UI", 10, "bold"),
                   variable=sifre_var, command=sifre_goster_gizle).pack()

    def kart_no_dogrula(no):
        return no.isdigit() and len(no) == 16

    def son_gecerlilik_dogrula(tarih):
        return bool(re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", tarih))

    def guvenlik_kodu_dogrula(kod):
        return kod.isdigit() and len(kod) == 3

    def kaydet_hesap():
        kullanici = entry_kullanici.get()
        sifre = entry_sifre.get()
        isim = entry_isim.get()
        soyisim = entry_soyisim.get()
        kart_no = entry_kart_no.get()
        son_gecerlilik = entry_son_gecerlilik.get()
        guvenlik_kodu = entry_guvenlik_kodu.get()

        if not (kullanici and sifre and isim and soyisim and kart_no and son_gecerlilik and guvenlik_kodu):
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
            return

        if kullanici in kullanicilar:
            messagebox.showerror("Hata", "Kullanıcı mevcut.")
            return

        for k, v in kullanicilar.items():
            if v.get("kart_no") == kart_no:
                messagebox.showerror("Hata", "Bu kart numarası başka bir kullanıcı tarafından kullanılıyor.")
                return

        if (not any(c.isupper() for c in sifre) or
            not any(c in string.punctuation for c in sifre) or
            not any(c.isdigit() for c in sifre)):
            messagebox.showerror("Hata", "Şifre en az bir büyük harf, bir özel karakter ve bir rakam içermelidir.")
            return

        if not kart_no_dogrula(kart_no):
            messagebox.showerror("Hata", "Kart numarası 16 haneli rakamlardan oluşmalıdır.")
            return

        if not son_gecerlilik_dogrula(son_gecerlilik):
            messagebox.showerror("Hata", "Son geçerlilik tarihi MM/YY formatında olmalıdır.")
            return

        if not guvenlik_kodu_dogrula(guvenlik_kodu):
            messagebox.showerror("Hata", "Güvenlik kodu 3 haneli rakam olmalıdır.")
            return

        kullanicilar[kullanici] = {
            "sifre": sifre,
            "isim": isim,
            "soyisim": soyisim,
            "kart_no": kart_no,
            "son_gecerlilik": son_gecerlilik,
            "guvenlik_kodu": guvenlik_kodu,
            "bakiye": 0,
            "para_birimi": "TRY",
            "gecmis": [],
            "eski_sifreler": []
        }

        kaydet()
        messagebox.showinfo("Başarılı", "Hesap oluşturuldu.")
        pencere.destroy()

    
    tk.Button(pencere, text="Kaydet", font=("Segoe UI", 10, "bold"), width=15, bg="#1565C0", fg="white", command=kaydet_hesap).pack(pady=5)
    tk.Button(pencere, text="Kapat", font=("Segoe UI", 10, "bold"), width=15, bg="#D32F2F", fg="white", command=pencere.destroy).pack(pady=5)
    tk.Button(pencere, text="Geri", font=("Segoe UI", 10, "bold"), width=15, bg="#90A4AE", fg="white", command=pencere.destroy).pack()
                                                                                                                   
# ----------------------------------GİRİŞ YAP EKRANI-------------------------------------
def giris_yap():
    pencere = tk.Toplevel()
    pencere.title("Giriş Yap")
    pencere.geometry("300x300")
    pencere.configure(bg="#E3F2FD")
    pencere.iconbitmap(r"C:\Users\ardaa\Desktop\ADVANCED PHYTON PROJESİ\b_abc_bank_logo.ico")


    
    tk.Label(pencere, text="Kullanıcı ID:", bg="#E3F2FD", font=("Segoe UI", 10, "bold")).pack()
    entry_kullanici = tk.Entry(pencere)
    entry_kullanici.pack()

    
    tk.Label(pencere, text="Şifre:", bg="#E3F2FD", font=("Segoe UI", 10, "bold")).pack()
    entry_sifre = tk.Entry(pencere, show="*")
    entry_sifre.pack()

    
    def giris_sifre_goster_gizle():
        entry_sifre.config(show="" if giris_sifre_var.get() else "*")

    giris_sifre_var = tk.BooleanVar()
    tk.Checkbutton(pencere, text="Şifreyi Göster", variable=giris_sifre_var,
                   command=giris_sifre_goster_gizle,bg="#E3F2FD",font=("Segoe UI", 10,"bold")).pack()

    
    def dogrula():
        kullanici = entry_kullanici.get()
        sifre = entry_sifre.get()
        if kullanici in kullanicilar and kullanicilar[kullanici].get("sifre") == sifre:
            messagebox.showinfo("Merhaba", f"Hoşgeldiniz {kullanicilar[kullanici].get('isim', 'Kullanıcı')}!")
            pencere.destroy()
            banka_ekrani(kullanici)
        else:
            messagebox.showerror("Hata", "Bilgiler yanlış.")

    
    def sifremi_unuttum():
        pencere_sifre = tk.Toplevel()
        pencere_sifre.title("Şifremi Unuttum")
        pencere_sifre.geometry("300x300")
        pencere_sifre.configure(bg="#E3F2FD")
        pencere.iconbitmap(r"C:\Users\ardaa\Desktop\ADVANCED PHYTON PROJESİ\b_abc_bank_logo.ico")


                               

        tk.Label(pencere_sifre, text="İsminiz:",bg="#E3F2FD",font=("Segoe UI", 10,"bold")).pack()
        entry_ad = tk.Entry(pencere_sifre)
        entry_ad.pack()

        tk.Label(pencere_sifre, text="Soyisminiz:",bg="#E3F2FD",font=("Segoe UI", 10,"bold")).pack()
        entry_soyad = tk.Entry(pencere_sifre)
        entry_soyad.pack()

        tk.Label(pencere_sifre, text="Kart Numarasının Son 4 Hanesi:",bg="#E3F2FD",font=("Segoe UI", 10,"bold")).pack()
        entry_kart_son4 = tk.Entry(pencere_sifre)
        entry_kart_son4.pack()

        tk.Label(pencere_sifre, text="Yeni Şifre:",bg="#E3F2FD",font=("Segoe UI", 10,"bold")).pack()
        entry_yeni_sifre = tk.Entry(pencere_sifre, show="*")
        entry_yeni_sifre.pack()

        def sifre_degistir():
            ad = entry_ad.get().strip().lower()
            soyad = entry_soyad.get().strip().lower()
            son4 = entry_kart_son4.get().strip()
            yeni_sifre = entry_yeni_sifre.get().strip()

            if not ad or not soyad or not son4 or not yeni_sifre:
                messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
                return

            for k, v in kullanicilar.items():
                if (
                    v.get("isim", "").lower() == ad and
                    v.get("soyisim", "").lower() == soyad and
                    v.get("kart_no", "").endswith(son4)
                ):
                    if yeni_sifre == v["sifre"]:
                        messagebox.showerror("Hata", "Yeni şifre, mevcut şifreyle aynı olamaz.")
                        return

                    if yeni_sifre in v.get("eski_sifreler", []):
                        messagebox.showerror("Hata", "Yeni şifre, son 3 şifreden biriyle aynı olamaz.")
                        return

                    v["eski_sifreler"] = [v["sifre"]] + v.get("eski_sifreler", [])[:2]
                    v["sifre"] = yeni_sifre
                    kaydet()
                    messagebox.showinfo("Başarılı", "Şifreniz güncellendi.")
                    pencere_sifre.destroy()
                    return

            messagebox.showerror("Hata", "Eşleşen kullanıcı bulunamadı.")

        tk.Button(pencere_sifre, text="Şifreyi Değiştir", font=("Segoe UI", 10,"bold"), width=15,
                  fg="white", bg="#1565C0", command=sifre_degistir).pack(pady=10)
        tk.Button(pencere_sifre, text="Geri", font=("Segoe UI", 10,"bold"), width=15,
                  fg="white", bg="#90A4AE", command=pencere_sifre.destroy).pack(pady=5)

    
    tk.Button(pencere, text="Giriş", font=("Segoe UI", 10,"bold"), width=15,
              fg="white", bg="#1976D2",command=dogrula).pack(pady=5)

    tk.Button(pencere, text="Şifremi Unuttum", font=("Segoe UI", 10,"bold"), width=15,
              fg="white", bg="#D32F2F",command=sifremi_unuttum).pack(pady=5)

    tk.Button(pencere, text="Geri", font=("Segoe UI", 10,"bold"), width=15,
              fg="white", bg="#90A4AE",command=pencere.destroy).pack()


#-----------------------------------BANKA EKRANI-------------------------------------
def banka_ekrani(kullanici):
    pencere = tk.Toplevel()
    pencere.title("Banka İşlemleri")
    pencere.geometry("650x650")
    pencere.configure(bg="#E3F2FD")
    pencere.iconbitmap(r"C:\Users\ardaa\Desktop\ADVANCED PHYTON PROJESİ\b_abc_bank_logo.ico")


    bilgiler = kullanicilar[kullanici]

    
    ana_frame = tk.Frame(pencere, bg="#E3F2FD")
    ana_frame.pack(fill="both", expand=True, padx=10, pady=10)

    sol_frame = tk.Frame(ana_frame, bg="#E3F2FD")
    sol_frame.pack(side="left", fill="both", expand=True)

    
    try:
        logo_path = r"C:\Users\ardaa\Desktop\ADVANCED PHYTON PROJESİ\c_abc_bank_logo.png"
        logo = Image.open(logo_path)
        logo = logo.resize((230, 230), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(pencere, image=logo_img, bg="#E3F2FD")
        logo_label.place(x=440, y=92)
        pencere.image = logo_img
    except Exception as e:
        print("Logo yüklenemedi:", repr(e))


    
    header_frame = tk.Frame(sol_frame, width=750, height=100, bg="#E3F2FD")
    header_frame.pack_propagate(0)
    header_frame.pack()

    merhaba_frame = tk.Frame(header_frame, bg="#E3F2FD")
    merhaba_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(merhaba_frame, text="Merhaba,", font=("Arial", 14, "bold"), bg="#E3F2FD").pack(side="left")
    tk.Label(merhaba_frame, text=f" {bilgiler['isim']} {bilgiler['soyisim']}", font=("Arial", 14), bg="#E3F2FD").pack(side="left")

    
    tk.Label(sol_frame, text="GENEL BİLGİLER:", font=("Arial", 13, "bold"), bg="#E3F2FD").pack(anchor="w", padx=3, pady=(7, 0))

    bilgiler_listesi = [
        ("Kullanıcı ID", kullanici),
        ("Kart Numarası", f"**** **** **** {bilgiler['kart_no'][-4:]}"),
        ("Son Geçerlilik Tarihi", bilgiler['son_gecerlilik']),
        ("Güvenlik Kodu", bilgiler['guvenlik_kodu']),
    ]

    for baslik, deger in bilgiler_listesi:
        satir = tk.Frame(sol_frame, bg="#E3F2FD")
        satir.pack(anchor="w", padx=3)
        tk.Label(satir, text=f"{baslik}:", font=("Arial", 12, "bold"), bg="#E3F2FD").pack(side="left")
        tk.Label(satir, text=f" {deger}", font=("Arial", 12), bg="#E3F2FD").pack(side="left")

    
    bakiye_vars = {
        "TRY": tk.StringVar(),
        "USD": tk.StringVar(),
        "EUR": tk.StringVar()
    }

    def bakiye_guncelle():
        bakiyeler = kullanicilar[kullanici].get("bakiye", {})
        if isinstance(bakiyeler, float) or isinstance(bakiyeler, int):
            bakiyeler = {"TRY": float(bakiyeler)}
        for birim in ["TRY", "USD", "EUR"]:
            bakiye = bakiyeler.get(birim, 0.0)
            bakiye_vars[birim].set(f"{birim} Bakiyesi: {bakiye:.2f}")

    bakiye_guncelle()

    for birim in ["TRY", "USD", "EUR"]:
           bakiye_satir = tk.Frame(sol_frame, bg="#E3F2FD")
           bakiye_satir.pack(anchor="w", padx=3, pady=2, fill="x")
           tk.Label(bakiye_satir, textvariable=bakiye_vars[birim], font=("Arial", 12, "bold"),fg="#1565C0", bg="#E3F2FD", anchor="w", justify="left").pack(side="left")

    def refresh():
        bakiye_guncelle()

    buton_font = ("Segoe UI", 12, "bold")
    buton_genislik = 20

    tk.Button(sol_frame, text="Para İşlemleri", font=buton_font, width=buton_genislik, fg="white", bg="#1565C0",
              command=lambda: para_penceresi(kullanici, refresh)).pack(pady=5)

    tk.Button(sol_frame, text="Döviz İşlemleri", font=buton_font, width=buton_genislik, fg="white", bg="#1565C0",
              command=lambda: doviz_penceresi(kullanici, refresh)).pack(pady=5)

    tk.Button(sol_frame, text="Havale İşlemleri", font=buton_font, width=buton_genislik, fg="white", bg="#1565C0",
              command=lambda: havale_penceresi(kullanici, refresh)).pack(pady=5)

    tk.Button(sol_frame, text="İşlem Geçmişi", font=buton_font, width=buton_genislik, fg="white", bg="#1565C0",
              command=lambda: gecmis_penceresi(kullanici)).pack(pady=5)

    tk.Button(sol_frame, text="Çıkış", font=buton_font, width=buton_genislik, fg="white", bg="#D32F2F",
              command=pencere_kapatma_onayi).pack(pady=10)

def pencere_kapatma_onayi():
        if messagebox.askyesno("Çıkış Onayı", "Programdan çıkmak istediğinize emin misiniz?"):
            kaydet()
            root.destroy()
            

def cikis():
    if messagebox.askyesno("Çıkış Onayı", "Programdan çıkmak istediğinize emin misiniz?"):
        kaydet()      
        root.destroy()  
        

def yukle():
    global kullanicilar
    try:
        if os.path.exists(DOSYA_ADI):
            with open(DOSYA_ADI, "r", encoding="utf-8") as f:
                icerik = f.read().strip()
                kullanicilar = json.loads(icerik) if icerik else {}
        else:
            kullanicilar = {}
    except Exception as e:
        print("Yükleme hatası:", e)
        kullanicilar = {}
#--------------------------------------ANA EKRAN----------------------------------------
root = tk.Tk()
root.title("ABC Bank")
root.geometry("400x300")
root.config(bg="#E3F2FD")
root.protocol("WM_DELETE_WINDOW", cikis)

root.iconbitmap(r"C:\Users\ardaa\Desktop\ADVANCED PHYTON PROJESİ\b_abc_bank_logo.ico")


tk.Label(root, text="ABC Bank'a Hoş Geldiniz", font=("Segoe UI", 20,"bold"),fg="black",bg="#E3F2FD").pack(pady=30)
tk.Button(root, text="Hesap Oluştur", width=20, font=("Segoe UI", 12,"bold"), fg="white",bg="#1565C0",command=hesap_olustur).pack(pady=10)
tk.Button(root, text="Giriş Yap", width=20, font=("Segoe UI", 12,"bold"), fg="white",bg="#64B5F6",command=giris_yap).pack(pady=10)
tk.Button(root, text="Çıkış", width=20, font=("Segoe UI", 12,"bold"), fg="white",bg="#D32F2F",command=cikis).pack(pady=10)

root.mainloop()

