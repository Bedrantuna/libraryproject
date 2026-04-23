# 🛡️ Siber Muhafız (Cyber Guardian) v18.1

Bu proje, kullanıcının bilgisayar başında olmadığı durumlarda iş istasyonunun fiziksel güvenliğini sağlamak amacıyla geliştirilmiş Python tabanlı bir izleme ve güvenlik sistemidir.

## 🚀 Özellikler
- **Gerçek Zamanlı İzleme:** OpenCV kütüphanesi kullanılarak kamera üzerinden hareket algılama.
- **Anlık Bildirim:** Yetkisiz bir erişim veya hareket tespit edildiğinde Telegram botu üzerinden kullanıcıya anlık fotoğraf ve mesaj gönderimi.
- **Sistem Takibi:** `psutil` ile sistem kaynaklarının izlenmesi ve şüpheli durumlarda uyarı mekanizması.
- **Kullanıcı Dostu Arayüz:** Tkinter kullanılarak geliştirilmiş yönetim paneli.
- **Giriş Engelleme:** Klavye ve fare hareketlerini takip ederek yetkisiz kullanım denemelerini kayıt altına alma.

## 🛠️ Kullanılan Teknolojiler
- **Dil:** Python 3.x
- **Kütüphaneler:** - `OpenCV`: Görüntü işleme ve hareket algılama.
  - `Telebot` (pyTelegramBotAPI): Telegram entegrasyonu.
  - `Tkinter`: GUI (Grafiksel Kullanıcı Arayüzü) tasarımı.
  - `Psutil`: Sistem ve süreç yönetimi.
  - `Threading`: Eş zamanlı arka plan taraması.

## 📦 Kurulum
Projenin çalışması için gerekli kütüphaneleri aşağıdaki komutla yükleyebilirsiniz:

```bash
pip install opencv-python pyTelegramBotAPI psutil
