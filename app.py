import requests
import time

# توكن البوت ومعرف القناة (تم تحديثه بالقيم التي قدمتها)
BOT_TOKEN = '6335197909:AAEVXGR2h3yNiThO3fwbBn_-AphOwnoItwE'  # توكن البوت
CHANNEL_ID = '-1002273356001'  # معرف القناة (رقمي)

# دالة لجلب قائمة السور
def fetch_surahs():
    url = "https://api.alquran.cloud/v1/surah"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print("فشل في جلب السور")
        return []

# دالة لجلب آيات سورة معينة
def fetch_ayahs(surah_number):
    url = f"https://api.alquran.cloud/v1/surah/{surah_number}/ar"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']['ayahs']
    else:
        print(f"فشل في جلب آيات السورة {surah_number}")
        return []

# دالة لجلب رابط التلاوة بصوت الشيخ المنشاوي
def fetch_audio_url(surah_number):
    url = f"https://api.alquran.cloud/v1/surah/{surah_number}/ar.alafasy"  # تغيير إلى الشيخ المنشاوي إذا كان متوفرًا
    response = requests.get(url)
    if response.status_code == 200:
        return [ayah['audio'] for ayah in response.json()['data']['ayahs']]
    else:
        print(f"فشل في جلب روابط التلاوة للسورة {surah_number}")
        return []

# دالة لإرسال الآية إلى تيليجرام
def send_ayah_to_telegram(surah_name, verse_num, ayah_text, audio_url):
    send_audio_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
    caption = f"سورة {surah_name} - الآية {verse_num}\n\n{ayah_text}"
    
    # جلب ملف الصوت
    audio_response = requests.get(audio_url)
    if audio_response.status_code != 200:
        print(f"فشل في جلب ملف الصوت للآية {verse_num}")
        return
    
    # إرسال الصوت إلى تيليجرام
    files = {'audio': ('ayah_audio.mp3', audio_response.content)}
    data = {'chat_id': CHANNEL_ID, 'caption': caption}
    response = requests.post(send_audio_url, files=files, data=data)
    
    if response.status_code == 200:
        print(f"تم إرسال الآية {verse_num} من سورة {surah_name} بنجاح")
    else:
        print(f"فشل في إرسال الآية {verse_num} من سورة {surah_name}: {response.text}")
        print(f"رابط الصوت: {audio_url}")
        print(f"التفاصيل: {response.json()}")

# دالة رئيسية لإرسال كل الآيات
def send_all_ayahs():
    surahs = fetch_surahs()
    for surah in surahs:
        surah_number = surah['number']
        surah_name = surah['name']
        ayahs = fetch_ayahs(surah_number)
        audio_urls = fetch_audio_url(surah_number)
        
        for ayah, audio_url in zip(ayahs, audio_urls):
            ayah_text = ayah['text']
            verse_num = ayah['numberInSurah']
            send_ayah_to_telegram(surah_name, verse_num, ayah_text, audio_url)
            time.sleep(2)  # تأخير بين كل آية لتجنب حظر التليجرام

# بدء الإرسال. 
if __name__ == "__main__":
    send_all_ayahs()  # إرسال جميع الآيات مرة واحدة
    print("تم إرسال جميع آيات القرآن الكريم بصوت الشيخ المنشاوي بنجاح!")
