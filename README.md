# ABC Bank Arayüz Uygulaması

Bu uygulama, kullanıcıların sanal bir banka arayüzü üzerinden döviz işlemleri, para yatırma/çekme, havale ve işlem geçmişini yönetmelerini sağlar.

## Gereksinimler

- Python 3.9+
- İnternet bağlantısı (döviz kuru için API kullanımı)
- Aşağıdaki Python kütüphaneleri:

```bash
pip install -r requirements.txt
```

## Kullanılan Kütüphaneler

- tkinter
- requests
- pillow

## Uygulamanın Çalıştırılması

```bash
python main.py
```

## Özellikler

- Hesap oluşturma ve giriş yapma
- Şifre sıfırlama
- Döviz dönüştürme
- Havale işlemleri
- İşlem geçmişi görüntüleme ve silme

## Notlar

- `kullanicilar.json` veritabanı dosyası otomatik olarak oluşur.
- Arayüzde kullanılan ikon ve görseller `assets/` klasöründe yer almalıdır.
