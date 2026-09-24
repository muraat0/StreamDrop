# StreamDrop Web Video & Audio Downloader

Modern, hızlı ve kullanıcı dostu bir arayüze sahip; **Flask** ve **yt-dlp** tabanlı yerel medya indirme aracı. Çeşitli sosyal medya platformlarından video ve ses içeriklerini çözünürlük seçimiyle indirmeyi ve arka planda **FFmpeg** entegrasyonuyla görüntü-ses akışlarını kayıpsız birleştirmeyi sağlar.

---

## 🌟 Öne Çıkan Özellikler

* **Geniş Platform Desteği:** X (Twitter), TikTok, Instagram, Vimeo ve daha birçok popüler video platformuyla tam uyumluluk.
* **Akıllı Akış Birleştirme (Muxing):** FFmpeg entegrasyonu sayesinde ayrık gelen yüksek çözünürlüklü görüntü ve ses akışlarını otomatik olarak birleştirir; sessiz video sorununu ortadan kaldırır.
* **Dinamik Çözünürlük ve Format Seçimi:** Kaynaktan alınan çözünürlükleri (1080p, 720p, 480p vb.) otomatik tespit eder ve doğrudan MP3 (yalnızca ses) indirme seçeneği sunar.
* **Canlı İlerleme Takibi (SSE):** Server-Sent Events mimarisiyle indirme yüzdesi, hız ve kalan süre bilgilerini arayüze canlı olarak aktarır.
* **Otomatik Önbellek Yönetimi:** İndirme tamamlanıp kullanıcı dosyayı teslim aldıktan sonra geçici dosyaları diskten temizleyerek yer kaplamasını önler.
* **Tek Tıkla Kurulum ve Başlatma:** Windows için hazırlanmış `.bat` betikleriyle bağımlılıkları otomatik kurar ve tarayıcıyı doğrudan açar.

---

## 🛠️ Kullanılan Teknolojiler

* **Backend:** Python 3, Flask
* **Çekirdek Motor:** `yt-dlp`
* **Medya İşleme:** FFmpeg
* **Asenkron Yapı:** Threading, Queue & Server-Sent Events (SSE)

---

## 📂 Proje Yapısı

```text
├── templates/
│   └── index.html          # Web arayüzü
├── server.py               # Flask API ve arka plan iş parçacığı yönetimi
├── requirements.txt        # Python bağımlılıkları
├── kurulum.bat             # Bağımlılıkları kuran kurulum betiği
├── baslat.bat              # Uygulamayı başlatan ve tarayıcıyı açan betik
├── ffmpeg.exe              # Medya işleme motoru (yerel dizin)
└── ffprobe.exe             # Akış analiz motoru (yerel dizin)

## 🎬 FFmpeg Kurulumu (Önemli)

Ses ve görüntünün kayıpsız birleştirilmesi ve MP3 dönüştürme işlemleri için projenin FFmpeg motoruna ihtiyacı vardır. Boyut sınırı nedeniyle bu dosyalar GitHub deposunda yer almaz. Aşağıdaki yöntemi kullanarak kolayca edinebilirsiniz:

### Taşınabilir (Portable) Kurulum Adımları
1. **[FFmpeg Release Essentials (.zip)](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)** bağlantısına tıklayarak güncel derlemeyi indirin.
2. İndirilen `.zip` arşivini açın ve içerisindeki `bin` klasörüne girin.
3. Orada bulunan **`ffmpeg.exe`** ve **`ffprobe.exe`** dosyalarını kopyalayıp doğrudan projenin ana dizinine (`server.py` dosyasının yanına) yapıştırın.
