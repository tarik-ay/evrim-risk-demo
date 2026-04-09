# Evrim AI — Pre-declaration Risk Scoring Demo

Gümrük beyannamesi gönderilmeden önce AI destekli risk analizi yapan demo uygulama.

## Ne yapar?
- Beyanname verilerini görüntüler (GTİP, menşe, kıymet, vergiler)
- AI risk analizi çalıştırır:
  - Kıymet emsal karşılaştırması
  - GTİP-mal tanımı uyum kontrolü
  - Belge tutarlılığı (fatura-beyanname-çeki listesi)
  - Mevzuat uyumu (TAREKS, TSE, EMY)
  - KKDF tasarruf fırsatı tespiti
- Risk skoru ve hat tahmini üretir
- Kritik sorunları ve önerileri listeler

## Çalıştırma

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Streamlit Community Cloud: share.streamlit.io → New app → repo seç → Deploy
