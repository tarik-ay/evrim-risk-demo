import streamlit as st
import time
import json

st.set_page_config(
    page_title="Evrim AI Risk Analizi",
    page_icon="🛃",
    layout="wide",
)

# --- Custom CSS ---
st.markdown("""
<style>
    .stApp { max-width: 900px; margin: 0 auto; }
    .risk-kritik { background: #FCEBEB; border: 1px solid #F09595; color: #791F1F; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
    .risk-uyari { background: #FAEEDA; border: 1px solid #FAC775; color: #633806; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
    .risk-ok { background: #EAF3DE; border: 1px solid #97C459; color: #27500A; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
    .evrim-uyari-kutusu { background: #FAEEDA; border: 1px solid #FAC775; border-radius: 8px; padding: 10px 14px; margin: 8px 0; font-size: 13px; color: #633806; }
    .kalem-kart { border: 1px solid #e0e0e0; border-radius: 10px; padding: 16px; margin-bottom: 12px; }
    .vergi-pill { background: #f0f0f0; border-radius: 6px; padding: 2px 8px; font-size: 12px; margin-right: 4px; display: inline-block; }
    .skor-kutusu { text-align: center; padding: 20px; }
    .skor-sayi { font-size: 48px; font-weight: 700; }
    .hat-bar { height: 8px; border-radius: 4px; margin: 4px 0; }
    .kontrol-kart { border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px; margin-bottom: 8px; }
    div[data-testid="stExpander"] { border: 1px solid #e0e0e0; border-radius: 10px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# --- Data ---
BEYANNAME = {
    "dosya_no": "26-30069",
    "kur_tarihi": "06.04.2026",
    "rejim": "4000 — Serbest Dolaşıma Giriş",
    "anlasma": "AT - Avrupa Topluluğu A.",
    "tasima": "1 - Deniz Yolu",
    "incoterms": "CIF Mersin",
    "doviz_kuru": "37,4520 TL/USD",
}

KALEMLER = [
    {
        "sno": 1,
        "gtip": "3926.90.97.90.29",
        "tanim": "Plastikten diğer eşya ve 39.01 ila 39.14 pozisyonlarında belirtilen diğer maddelerden eşya",
        "ticari_tanim": "İşghjkl",
        "mense": "🇮🇹 İtalya",
        "miktar": "50 Adet",
        "kalem_fiyati": "900,00 TL",
        "ist_kiymet": "1.017,00 TL",
        "agirlik": "Brüt 100 kg / Net 50 kg",
        "vergiler": [
            ("10 — Gümrük Vergisi", "45.267,38 TL", "0%", "0,00 TL"),
            ("40 — KDV", "49.666,43 TL", "10%", "4.966,64 TL"),
            ("89 — EMY", "—", "—", "1.605,80 TL"),
            ("KF — KKDF", "39.987,54 TL", "6%", "2.399,25 TL"),
        ],
        "uyarilar": [
            "ASGARİ FİYAT: 5,5 $/KG(B)",
            "V Sayılı Listeye tabidir. Ürün Cinsine Göre Değişir",
            "Tarım ve Orman Bakanlığı Denetimi ! (2026/5) ÜG",
            "TAREKS Denetimi ! (2026/12) ÜGD Kapsamında",
            "Ek Mali Yükümlülük Vergisi'ne tabidir",
        ],
    },
    {
        "sno": 2,
        "gtip": "8544.49.93.00.19",
        "tanim": "PVC izoleli bakır kablo, 2.5mm², 1000V altı",
        "ticari_tanim": "PVC insulated copper cable 2.5mm²",
        "mense": "🇨🇳 Çin",
        "miktar": "15.000 Metre",
        "kalem_fiyati": "21.000,00 USD",
        "ist_kiymet": "23.520,00 USD",
        "agirlik": "Brüt 4.200 kg / Net 3.800 kg",
        "vergiler": [
            ("10 — Gümrük Vergisi", "787.320,00 TL", "3,7%", "29.130,84 TL"),
            ("40 — KDV", "816.450,84 TL", "20%", "163.290,17 TL"),
        ],
        "uyarilar": [
            "TSE Uygunluk Belgesi Zorunlu",
        ],
    },
]

RISK_CHECKS = [
    {
        "kategori": "Kıymet kontrolü",
        "baslik": "Kalem 1 — Birim fiyat emsal karşılaştırması",
        "aciklama": "Birim fiyat 18,00 $/kg. Asgari fiyat 5,5 $/kg. Emsal aralık: 4,80–22,00 $/kg. **Fiyat emsal dahilinde.**",
        "detay": "Son 90 günde aynı GTİP'ten 147 beyanname analiz edildi. Medyan birim fiyat: 12,40 $/kg. Beyan edilen fiyat ortalamanın üzerinde — düşük kıymet riski yok.",
        "durum": "ok",
    },
    {
        "kategori": "Kıymet kontrolü",
        "baslik": "Kalem 2 — Birim fiyat emsal karşılaştırması",
        "aciklama": "Birim fiyat 1,40 $/m. Emsal aralık: 0,95–2,10 $/m. **Fiyat emsal dahilinde.**",
        "detay": "Çin menşeli bakır kablo (8544.49) için son 90 günde 312 beyanname. Medyan: 1,55 $/m. Beyan edilen fiyat medyana yakın.",
        "durum": "ok",
    },
    {
        "kategori": "Kıymet kontrolü",
        "baslik": "KKDF uygulaması kontrolü",
        "aciklama": "Kalem 1'de KF satırında **2.399,25 TL** KKDF hesaplanmış. Ödeme vadeli görünüyor. Peşin ödeme yapıldıysa bu tutar sıfırlanabilir.",
        "detay": "Peşin ödeme dekontu (SWIFT) varsa KKDF muafiyeti uygulanabilir. Firmadan ödeme dekontu talep edilmeli. **Potansiyel tasarruf: 2.399,25 TL.**",
        "durum": "uyari",
    },
    {
        "kategori": "GTİP doğrulama",
        "baslik": "Kalem 1 — Ticari tanım alanı boş/anlamsız",
        "aciklama": "Ticari tanım: **'İşghjkl'** — bu anlamsız bir giriş. Gümrük memuru bu alanı ilk kontrol eder. **Kırmızı hat riski yüksek.**",
        "detay": "Ticari tanım alanı gümrük muayene memurunun malı tanımlayabilmesi için kritik. Anlamlı bir tanım girilmeli: ör. 'Plastik montaj klipsi', 'Plastik boru bağlantı parçası', 'Plastik dekoratif aksesuar' vb. Bu alan düzeltilmeden beyanname gönderilmemeli.",
        "durum": "kritik",
    },
    {
        "kategori": "GTİP doğrulama",
        "baslik": "Kalem 2 — GTİP-mal tanımı uyumu",
        "aciklama": "GTİP 8544.49.93.00.19 — 'Bakır iletkenli, PVC izoleli kablo, 1000V altı'. Mal tanımı ile **uyumlu.**",
        "detay": "Faturada belirtilen voltaj sınıfı 0.6/1kV — 1000V sınırında. 8544.49 altında doğru konumlanmış. Alternatif 8544.60 (1000V üstü) gerekmez.",
        "durum": "ok",
    },
    {
        "kategori": "Belge tutarlılığı",
        "baslik": "Fatura–beyanname tutar çaprazlaması",
        "aciklama": "Fatura toplamı (CIF): 56.550 USD. Beyanname toplam kıymet: 56.537 USD. Fark: 13 USD (%0,02). **Kabul edilebilir.**",
        "detay": "Yuvarlama farklarından kaynaklanan minimal sapma. %1 üzeri fark olsaydı uyarı verilecekti.",
        "durum": "ok",
    },
    {
        "kategori": "Belge tutarlılığı",
        "baslik": "Ağırlık tutarlılığı — UYUMSUZLUK",
        "aciklama": "Çeki listesi brüt: 8.450 kg. Beyanname toplam brüt (K1 + K2): 4.300 kg. **Fark: 4.150 kg.** Büyük uyumsuzluk!",
        "detay": "Olası sebepler: (1) Henüz girilmemiş kalemler var, (2) Çeki listesi ile beyanname arasında gerçek hata. Tüm kalemler girildikten sonra toplam ağırlık mutlaka tekrar kontrol edilmeli. Bu fark kırmızı hat sebebidir.",
        "durum": "kritik",
    },
    {
        "kategori": "Mevzuat uyumu",
        "baslik": "TAREKS denetimi gerekliliği",
        "aciklama": "Kalem 1: GTİP 3926.90 — **TAREKS (2026/12) ÜGD kapsamında.** TAREKS referans numarası beyannamede girilmeli.",
        "detay": "TAREKS başvurusu yapılmış mı kontrol edilmeli. Referans numarası olmadan beyanname BİLGE'de tescil edilemez. Firma TAREKS portalından başvuru yapmalı.",
        "durum": "uyari",
    },
    {
        "kategori": "Mevzuat uyumu",
        "baslik": "TSE belgesi kontrolü",
        "aciklama": "Kalem 2: GTİP 8544.49 — **TSE uygunluk belgesi zorunlu.** Belge dosyada mevcut mu kontrol edilmeli.",
        "detay": "TSE belgesi numarası beyanname ek belgeler bölümüne girilmeli. Belge süresi dolmuş olabilir — geçerlilik tarihi kontrol edilmeli.",
        "durum": "uyari",
    },
    {
        "kategori": "Mevzuat uyumu",
        "baslik": "Ek mali yükümlülük (EMY) doğrulama",
        "aciklama": "Kalem 1: EMY'ye tabi. Vergi satırında 89 kodlu **1.605,80 TL** hesaplanmış. Güncel oran ile doğrulanmalı.",
        "detay": "2026 yılı güncel EMY oranları ile karşılaştırma yapıldı. Tutar makul görünüyor ancak Cumhurbaşkanlığı kararnamesi referansı (tarih ve sayı) kontrol edilmeli.",
        "durum": "uyari",
    },
]


def badge_html(durum):
    css_class = f"risk-{durum}"
    labels = {"kritik": "KRİTİK", "uyari": "UYARI", "ok": "SORUNSUZ"}
    return f'<span class="{css_class}">{labels[durum]}</span>'


def icon_for(durum):
    return {"kritik": "🔴", "uyari": "🟡", "ok": "🟢"}[durum]


# --- Header ---
st.markdown("### 🛃 Evrim AI — Pre-declaration risk scoring")
st.caption("Demo: Beyanname verisi üzerinde AI risk analizi")

tab1, tab2 = st.tabs(["📋 Beyanname verisi", "🔍 Risk analizi"])

# --- Tab 1: Beyanname ---
with tab1:
    st.markdown("##### Dosya bilgileri")
    col1, col2, col3 = st.columns(3)
    col1.metric("Dosya no", BEYANNAME["dosya_no"])
    col2.metric("Kur tarihi", BEYANNAME["kur_tarihi"])
    col3.metric("Döviz kuru", BEYANNAME["doviz_kuru"])

    col4, col5, col6 = st.columns(3)
    col4.metric("Rejim", "4000")
    col5.metric("Taşıma şekli", "Deniz Yolu")
    col6.metric("Incoterms", "CIF Mersin")

    st.markdown("---")
    st.markdown("##### Kalemler")

    for k in KALEMLER:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Kalem {k['sno']}** — `{k['gtip']}`")
                st.caption(k["tanim"])
                if k["ticari_tanim"]:
                    st.text(f"Ticari tanım: {k['ticari_tanim']}")
            with c2:
                st.markdown(f"**Menşe:** {k['mense']}")
                st.markdown(f"**Miktar:** {k['miktar']}")

            m1, m2, m3 = st.columns(3)
            m1.metric("Kalem fiyatı", k["kalem_fiyati"])
            m2.metric("İst. kıymet", k["ist_kiymet"])
            m3.metric("Ağırlık", k["agirlik"])

            if k["vergiler"]:
                st.markdown("**Vergiler:**")
                vergi_data = {"Vergi türü": [], "Matrah": [], "Oran": [], "Tutar": []}
                for v in k["vergiler"]:
                    vergi_data["Vergi türü"].append(v[0])
                    vergi_data["Matrah"].append(v[1])
                    vergi_data["Oran"].append(v[2])
                    vergi_data["Tutar"].append(v[3])
                st.dataframe(vergi_data, hide_index=True, use_container_width=True)

            if k["uyarilar"]:
                uyari_text = "<br>".join([f"⚠️ {u}" for u in k["uyarilar"]])
                st.markdown(f'<div class="evrim-uyari-kutusu">{uyari_text}</div>', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🚀 AI risk analizi çalıştır", type="primary", use_container_width=True):
        st.session_state["run_analysis"] = True
        st.switch_page_or_rerun = True

# --- Tab 2: Risk Analizi ---
with tab2:

    run = st.session_state.get("run_analysis", False)

    if not run:
        st.info("Henüz analiz yapılmadı. **Beyanname verisi** sekmesine gidip **AI risk analizi çalıştır** butonuna basın.")
    else:
        # Animated progress
        if "analysis_done" not in st.session_state:
            progress_bar = st.progress(0, text="Risk kontrolleri çalıştırılıyor...")
            for i in range(len(RISK_CHECKS)):
                time.sleep(0.25)
                progress_bar.progress(
                    (i + 1) / len(RISK_CHECKS),
                    text=f"Kontrol {i+1}/{len(RISK_CHECKS)}: {RISK_CHECKS[i]['kategori']}..."
                )
            progress_bar.empty()
            st.session_state["analysis_done"] = True

        # Score + Hat
        st.markdown("##### Özet")
        s1, s2, s3, s4, s5 = st.columns(5)

        risk_score = 42
        kritik = sum(1 for c in RISK_CHECKS if c["durum"] == "kritik")
        uyari = sum(1 for c in RISK_CHECKS if c["durum"] == "uyari")
        ok = sum(1 for c in RISK_CHECKS if c["durum"] == "ok")

        s1.metric("Risk skoru", f"{risk_score}/100")
        s2.metric("Hat tahmini", "Sarı hat")
        s3.metric("Kritik", kritik)
        s4.metric("Uyarı", uyari)
        s5.metric("Sorunsuz", ok)

        st.markdown("---")

        # Hat distribution
        st.markdown("##### Hat olasılık dağılımı")
        hat_col1, hat_col2, hat_col3, hat_col4 = st.columns(4)
        hat_col1.progress(10, text="Yeşil %10")
        hat_col2.progress(25, text="Mavi %25")
        hat_col3.progress(45, text="Sarı %45")
        hat_col4.progress(20, text="Kırmızı %20")

        st.markdown("---")

        # Kontroller
        st.markdown("##### Detaylı kontroller")

        # Group by status
        kritik_checks = [c for c in RISK_CHECKS if c["durum"] == "kritik"]
        uyari_checks = [c for c in RISK_CHECKS if c["durum"] == "uyari"]
        ok_checks = [c for c in RISK_CHECKS if c["durum"] == "ok"]

        if kritik_checks:
            st.markdown(f"🔴 **Kritik sorunlar** ({len(kritik_checks)})")
            for check in kritik_checks:
                with st.expander(f"❌ {check['baslik']}"):
                    st.markdown(check["aciklama"])
                    st.divider()
                    st.caption("💡 Detaylı analiz")
                    st.markdown(check["detay"])

        if uyari_checks:
            st.markdown(f"🟡 **Uyarılar** ({len(uyari_checks)})")
            for check in uyari_checks:
                with st.expander(f"⚠️ {check['baslik']}"):
                    st.markdown(check["aciklama"])
                    st.divider()
                    st.caption("💡 Detaylı analiz")
                    st.markdown(check["detay"])

        if ok_checks:
            st.markdown(f"🟢 **Sorunsuz** ({len(ok_checks)})")
            for check in ok_checks:
                with st.expander(f"✅ {check['baslik']}"):
                    st.markdown(check["aciklama"])
                    st.divider()
                    st.caption("💡 Detaylı analiz")
                    st.markdown(check["detay"])

        st.markdown("---")

        # Özet öneri
        st.markdown("##### 📌 AI önerisi")
        st.warning("""
        **Beyanname gönderilmeden önce 2 kritik sorun çözülmeli:**

        1. **Ticari tanım alanı düzeltilmeli** — 'İşghjkl' yerine anlamlı bir ürün tanımı girilmeli (ör: 'Plastik montaj klipsi'). Bu alan gümrük memurunun ilk kontrol noktasıdır.

        2. **Ağırlık uyumsuzluğu giderilmeli** — Çeki listesi brüt ağırlığı (8.450 kg) ile beyanname toplamı (4.300 kg) arasında 4.150 kg fark var. Tüm kalemler girilip toplam doğrulanmalı.

        **Ayrıca 4 uyarı takip edilmeli:** KKDF tasarruf fırsatı (2.399 TL), TAREKS referans numarası, TSE belgesi ve EMY oranı doğrulaması.
        """)

        # Reset
        if st.button("🔄 Yeniden analiz et"):
            del st.session_state["analysis_done"]
            del st.session_state["run_analysis"]
            st.rerun()
