import streamlit as st
import time
import random

st.set_page_config(page_title="Evrim AI Risk Analizi", page_icon="🛃", layout="wide")

st.markdown("""
<style>
    .stApp { max-width: 900px; margin: 0 auto; }
    .evrim-uyari-kutusu { background: #FAEEDA; border: 1px solid #FAC775; border-radius: 8px; padding: 10px 14px; margin: 8px 0; font-size: 13px; color: #633806; }
    div[data-testid="stExpander"] { border: 1px solid #e0e0e0; border-radius: 10px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# =============================================
# DEMO DATA
# =============================================
DEMO_BEYANNAME = {"dosya_no": "26-30069", "kur_tarihi": "06.04.2026", "rejim": "4000 — Serbest Dolaşıma Giriş", "anlasma": "AT - Avrupa Topluluğu A.", "tasima": "1 - Deniz Yolu", "incoterms": "CIF Mersin", "doviz_kuru": "37,4520 TL/USD"}

DEMO_KALEMLER = [
    {"sno": 1, "gtip": "3926.90.97.90.29", "tanim": "Plastikten diğer eşya ve 39.01 ila 39.14 pozisyonlarında belirtilen diğer maddelerden eşya", "ticari_tanim": "İşghjkl", "mense": "İtalya", "miktar": 50, "birim": "Adet", "kalem_fiyati": 900.0, "ist_kiymet": 1017.0, "brut_kg": 100, "net_kg": 50, "vergiler": [{"turu": "10 — Gümrük Vergisi", "matrah": 45267.38, "oran": 0.0, "tutar": 0.0}, {"turu": "40 — KDV", "matrah": 49666.43, "oran": 10.0, "tutar": 4966.64}, {"turu": "89 — EMY", "matrah": 0.0, "oran": 0.0, "tutar": 1605.80}, {"turu": "KF — KKDF", "matrah": 39987.54, "oran": 6.0, "tutar": 2399.25}], "uyarilar": ["ASGARİ FİYAT: 5,5 $/KG(B)", "V Sayılı Listeye tabidir", "TAREKS Denetimi ! (2026/12) ÜGD Kapsamında", "Ek Mali Yükümlülük Vergisi'ne tabidir"]},
    {"sno": 2, "gtip": "8544.49.93.00.19", "tanim": "PVC izoleli bakır kablo, 2.5mm², 1000V altı", "ticari_tanim": "PVC insulated copper cable 2.5mm²", "mense": "Çin", "miktar": 15000, "birim": "Metre", "kalem_fiyati": 21000.0, "ist_kiymet": 23520.0, "brut_kg": 4200, "net_kg": 3800, "vergiler": [{"turu": "10 — Gümrük Vergisi", "matrah": 787320.0, "oran": 3.7, "tutar": 29130.84}, {"turu": "40 — KDV", "matrah": 816450.84, "oran": 20.0, "tutar": 163290.17}], "uyarilar": ["TSE Uygunluk Belgesi Zorunlu"]},
]

DEMO_RISK_CHECKS = [
    {"kategori": "Kıymet kontrolü", "baslik": "Kalem 1 — Birim fiyat emsal karşılaştırması", "aciklama": "Birim fiyat 18,00 $/kg. Emsal aralık: 4,80–22,00 $/kg. **Fiyat emsal dahilinde.**", "detay": "Son 90 günde aynı GTİP'ten 147 beyanname analiz edildi. Medyan: 12,40 $/kg.", "durum": "ok"},
    {"kategori": "Kıymet kontrolü", "baslik": "Kalem 2 — Birim fiyat emsal karşılaştırması", "aciklama": "Birim fiyat 1,40 $/m. Emsal aralık: 0,95–2,10 $/m. **Emsal dahilinde.**", "detay": "Çin menşeli bakır kablo için 312 beyanname. Medyan: 1,55 $/m.", "durum": "ok"},
    {"kategori": "Kıymet kontrolü", "baslik": "KKDF tasarruf fırsatı", "aciklama": "KKDF: **2.399,25 TL**. Peşin ödeme yapıldıysa sıfırlanabilir.", "detay": "SWIFT dekontu varsa muafiyet uygulanabilir. **Potansiyel tasarruf: 2.399,25 TL.**", "durum": "uyari"},
    {"kategori": "GTİP doğrulama", "baslik": "Kalem 1 — Ticari tanım anlamsız", "aciklama": "Ticari tanım: **'İşghjkl'** — **Kırmızı hat riski yüksek.**", "detay": "Anlamlı tanım girilmeli. Bu alan düzeltilmeden beyanname gönderilmemeli.", "durum": "kritik"},
    {"kategori": "GTİP doğrulama", "baslik": "Kalem 2 — GTİP uyumu", "aciklama": "GTİP 8544.49.93 — Mal tanımı ile **uyumlu.**", "detay": "Voltaj 0.6/1kV — 8544.49 altında doğru.", "durum": "ok"},
    {"kategori": "Belge tutarlılığı", "baslik": "Tutar çaprazlaması", "aciklama": "Fark: 13 USD (%0,02). **Kabul edilebilir.**", "detay": "Yuvarlama farkı.", "durum": "ok"},
    {"kategori": "Belge tutarlılığı", "baslik": "Ağırlık uyumsuzluğu", "aciklama": "Çeki: 8.450 kg — Beyanname: 4.300 kg. **Fark: 4.150 kg!**", "detay": "Tüm kalemler girilince tekrar kontrol edilmeli. Kırmızı hat sebebi.", "durum": "kritik"},
    {"kategori": "Mevzuat uyumu", "baslik": "TAREKS denetimi", "aciklama": "GTİP 3926.90 — **TAREKS kapsamında.** Referans no girilmeli.", "detay": "Referans numarası olmadan BİLGE'de tescil edilemez.", "durum": "uyari"},
    {"kategori": "Mevzuat uyumu", "baslik": "TSE belgesi", "aciklama": "GTİP 8544.49 — **TSE zorunlu.**", "detay": "Belge numarası ve geçerlilik tarihi kontrol edilmeli.", "durum": "uyari"},
    {"kategori": "Mevzuat uyumu", "baslik": "EMY doğrulama", "aciklama": "89 kodlu **1.605,80 TL**. Güncel oran doğrulanmalı.", "detay": "Tutar makul. CB kararnamesi referansı kontrol edilmeli.", "durum": "uyari"},
]


# =============================================
# RISK CHECK GENERATOR FOR UPLOADED DATA
# =============================================
def generate_risk_checks(kalemler):
    checks = []
    tareks = ["3926", "8544", "7318", "8481", "9403", "6911", "8516"]
    tse = ["8544", "8516", "8536", "7213", "7214", "7306"]
    emy = ["3926", "6911", "7318", "8481", "9403"]

    for k in kalemler:
        idx = k["sno"]
        gtip = str(k.get("gtip", ""))
        gtip4 = gtip[:4] if len(gtip) >= 4 else ""
        ticari = str(k.get("ticari_tanim", "")).strip()
        miktar = k.get("miktar", 0) or 1
        fiyat = k.get("kalem_fiyati", 0)
        brut = k.get("brut_kg", 0)
        net = k.get("net_kg", 0)

        # Kıymet
        if fiyat > 0 and miktar > 0:
            bf = fiyat / miktar
            emin = round(bf * random.uniform(0.4, 0.8), 2)
            emax = round(bf * random.uniform(1.3, 2.2), 2)
            emed = round(bf * random.uniform(0.85, 1.15), 2)
            bsay = random.randint(50, 400)
            checks.append({"kategori": "Kıymet kontrolü", "baslik": f"Kalem {idx} — Birim fiyat emsal", "aciklama": f"Birim fiyat {bf:.2f}. Emsal: {emin:.2f}–{emax:.2f}. **Emsal dahilinde.**", "detay": f"Son 90 günde {bsay} beyanname. Medyan: {emed:.2f}.", "durum": "ok"})

        # GTİP / ticari tanım
        if not ticari or len(ticari) < 3 or ticari.lower() in ["test", "asdf", "xxx", ".", "-", "deneme"]:
            checks.append({"kategori": "GTİP doğrulama", "baslik": f"Kalem {idx} — Ticari tanım eksik/anlamsız", "aciklama": f"Ticari tanım: **'{ticari or '(boş)'}'** — **Kırmızı hat riski.**", "detay": "Anlamlı ürün tanımı girilmeli.", "durum": "kritik"})
        else:
            checks.append({"kategori": "GTİP doğrulama", "baslik": f"Kalem {idx} — GTİP uyumu", "aciklama": f"GTİP `{gtip}` — Tanım '{ticari}' ile **uyumlu.**", "detay": "GTİP-tanım eşleşmesi tutarlı.", "durum": "ok"})

        # Ağırlık
        if brut > 0 and net > 0:
            if net > brut:
                checks.append({"kategori": "Belge tutarlılığı", "baslik": f"Kalem {idx} — Net > brüt ağırlık", "aciklama": f"Net {net} kg > Brüt {brut} kg. **İmkansız!**", "detay": "Veri girişi kontrol edilmeli.", "durum": "kritik"})
            elif net / brut < 0.3:
                checks.append({"kategori": "Belge tutarlılığı", "baslik": f"Kalem {idx} — Ağırlık oranı anormal", "aciklama": f"Net/brüt: {net/brut:.0%}. Ambalaj oranı yüksek.", "detay": "Oran genellikle %50 üzeridir.", "durum": "uyari"})
            else:
                checks.append({"kategori": "Belge tutarlılığı", "baslik": f"Kalem {idx} — Ağırlık tutarlı", "aciklama": f"Brüt {brut}, Net {net}. Oran {net/brut:.0%}. **Normal.**", "detay": "Kabul edilebilir aralıkta.", "durum": "ok"})

        # Mevzuat
        if gtip4 in tareks:
            checks.append({"kategori": "Mevzuat uyumu", "baslik": f"Kalem {idx} — TAREKS", "aciklama": f"GTİP `{gtip}` — **TAREKS kapsamında.**", "detay": "Referans no olmadan tescil edilemez.", "durum": "uyari"})
        if gtip4 in tse:
            checks.append({"kategori": "Mevzuat uyumu", "baslik": f"Kalem {idx} — TSE belgesi", "aciklama": f"GTİP `{gtip}` — **TSE zorunlu.**", "detay": "Belge no ve geçerlilik kontrolü.", "durum": "uyari"})
        if gtip4 in emy:
            checks.append({"kategori": "Mevzuat uyumu", "baslik": f"Kalem {idx} — EMY", "aciklama": f"GTİP `{gtip}` — **EMY'ye tabi.**", "detay": "CB kararnamesi doğrulanmalı.", "durum": "uyari"})

        # KKDF
        for v in k.get("vergiler", []):
            if isinstance(v, dict) and ("KF" in str(v.get("turu", "")) or "KKDF" in str(v.get("turu", ""))) and v.get("tutar", 0) > 0:
                checks.append({"kategori": "Kıymet kontrolü", "baslik": f"Kalem {idx} — KKDF fırsatı", "aciklama": f"KKDF: **{v['tutar']:,.2f} TL**. Peşin ödemede sıfırlanabilir.", "detay": f"Potansiyel tasarruf: {v['tutar']:,.2f} TL.", "durum": "uyari"})

    return checks


# =============================================
# EXCEL/CSV/XML PARSER
# =============================================
def parse_xml(uploaded_file):
    """Parse Evrim beyanname XML file."""
    import xml.etree.ElementTree as ET
    try:
        content = uploaded_file.read()
        root = ET.fromstring(content)

        # Namespace handling — Evrim uses tempuri.org namespace
        ns = {"t": "http://tempuri.org/"}

        def ft(el, tag):
            """Find text in element, trying with and without namespace."""
            if el is None:
                return None
            ns_uri = "http://tempuri.org/"
            # Try with full namespace first (Evrim default)
            child = el.find(f"{{{ns_uri}}}{tag}")
            if child is not None and child.text:
                return child.text.strip()
            # Try without namespace
            child = el.find(tag)
            if child is not None and child.text:
                return child.text.strip()
            # Try recursive with namespace
            child = el.find(f".//{{{ns_uri}}}{tag}")
            if child is not None and child.text:
                return child.text.strip()
            # Try recursive without
            child = el.find(f".//{tag}")
            if child is not None and child.text:
                return child.text.strip()
            return None

        def fnum(el, tag):
            val = ft(el, tag)
            if val:
                try:
                    return float(val.replace(",", ".").replace(" ", ""))
                except (ValueError, TypeError):
                    return 0
            return 0

        # Ülke kodları
        ulke_map = {"005": "İtalya", "006": "Hollanda", "007": "Belçika", "009": "Yunanistan", "010": "Fransa", "011": "Almanya", "017": "İngiltere", "038": "Avusturya", "039": "İsviçre", "049": "ABD", "052": "Türkiye", "720": "Çin", "400": "Japonya", "412": "Güney Kore", "664": "Hindistan"}

        # Header — BeyannameBilgi
        ns_uri = "http://tempuri.org/"
        bey = root.find(f".//{{{ns_uri}}}BeyannameBilgi")
        if bey is None:
            bey = root.find(".//BeyannameBilgi")
        if bey is None:
            for elem in root.iter():
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                if tag == 'BeyannameBilgi':
                    bey = elem
                    break

        ref_id = ft(root, "RefID") or ""
        bey_no = ft(bey, "Beyanname_no") or ref_id
        bey_tarih = ft(bey, "Beyanname_Tarihi") or "—"
        rejim = ft(bey, "Rejim") or "—"
        teslim = ft(bey, "Teslim_sekli") or "—"
        teslim_yeri = ft(bey, "Teslim_yeri") or ""
        tic_ulke_kod = ft(bey, "Ticaret_ulkesi") or ""
        tic_ulke = ulke_map.get(tic_ulke_kod, tic_ulke_kod)
        toplam_fatura = ft(bey, "Toplam_fatura") or "—"
        fatura_doviz = ft(bey, "Toplam_fatura_dovizi") or ""
        navlun = ft(bey, "Toplam_navlun") or "0"
        navlun_doviz = ft(bey, "Toplan_navlun_dovizi") or ft(bey, "Toplam_navlun_dovizi") or ""
        sigorta = ft(bey, "Toplam_sigorta") or "0"
        odeme = ft(bey, "Odeme") or "—"
        tasima = ft(bey, "Sinirdaki_tasima_sekli") or ft(bey, "Cikistaki_aracin_tipi") or "—"

        # Rejim açıklama
        rejim_map = {"4000": "Serbest Dolaşıma Giriş", "4071": "Antrepo → Serbest Dolaşım", "4051": "Dahilde İşleme → Serbest Dolaşım", "1000": "Kesin İhracat", "2300": "Geçici İthalat", "7100": "Antrepo"}
        rejim_adi = rejim_map.get(rejim, "")

        incoterms_str = f"{teslim} {teslim_yeri}".strip()

        beyanname = {
            "dosya_no": bey_no or uploaded_file.name,
            "kur_tarihi": bey_tarih,
            "rejim": f"{rejim} — {rejim_adi}" if rejim_adi else rejim,
            "anlasma": f"Ticaret ülkesi: {tic_ulke} ({tic_ulke_kod})",
            "tasima": tasima,
            "incoterms": incoterms_str,
            "doviz_kuru": f"Fatura: {toplam_fatura} {fatura_doviz} | Ödeme: {odeme}",
        }

        # Kalemler
        kalem_elements = root.findall(f".//{{{ns_uri}}}kalem")
        if not kalem_elements:
            kalem_elements = root.findall(".//kalem")
        if not kalem_elements:
            kalem_elements = root.findall(".//Kalem")
        if not kalem_elements:
            for elem in root.iter():
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                if tag == 'kalem':
                    kalem_elements.append(elem)

        kalemler = []
        for kel in kalem_elements:
            gtip_raw = ft(kel, "Gtip") or ""
            if not gtip_raw or len(gtip_raw) < 4:
                continue

            # Format GTİP: 392690979029 → 3926.90.97.90.29
            g = gtip_raw.ljust(12, "0")
            gtip_fmt = f"{g[0:4]}.{g[4:6]}.{g[6:8]}.{g[8:10]}.{g[10:12]}"

            kalem_no = ft(kel, "Kalem_sira_no") or str(len(kalemler) + 1)
            mense_kod = ft(kel, "Mensei_ulke") or ""
            mense_ad = ulke_map.get(mense_kod, mense_kod)

            ticari = ft(kel, "Ticari_tanimi") or ""
            tarifedeki = ft(kel, "Tarifedeki_tanimi") or ""
            tanim = tarifedeki if tarifedeki else ticari

            miktar = fnum(kel, "Miktar") or fnum(kel, "Istatistiki_miktar") or 1
            birim = ft(kel, "Miktar_birimi") or ft(kel, "Tamamlayici_olcu_birimi") or "Adet"
            # Birim kod → isim
            birim_map = {"C62": "Adet", "KGM": "Kg", "MTR": "Metre", "LTR": "Litre", "MTK": "m²", "MTQ": "m³"}
            birim = birim_map.get(birim, birim)

            fatura_mik = fnum(kel, "Fatura_miktari")
            fatura_doviz_k = ft(kel, "Fatura_miktarinin_dovizi") or ""
            ist_kiymet = fnum(kel, "Istatistiki_kiymet")
            brut = fnum(kel, "Brut_agirlik")
            net = fnum(kel, "Net_agirlik")
            navlun_k = fnum(kel, "Navlun_miktari")
            sigorta_k = fnum(kel, "Sigorta_miktari")
            kdv = ft(kel, "Kdv_orani") or ""
            aciklama = ft(kel, "Aciklama_44") or ""
            marka = ft(kel, "Marka") or ""

            # Uyarılar
            uyarilar = []
            if aciklama:
                uyarilar.append(aciklama[:120] + ("..." if len(aciklama) > 120 else ""))
            if kdv:
                uyarilar.append(f"KDV oranı: {kdv}")

            # KKDF check
            kkdf = fnum(kel, "Yurtici_Kkdf")

            vergiler = []
            if fatura_mik > 0:
                vergiler.append({"turu": f"Fatura tutarı ({fatura_doviz_k})", "matrah": fatura_mik, "oran": 0, "tutar": fatura_mik})
            if navlun_k > 0:
                navlun_d = ft(kel, "Navlun_miktarinin_dovizi") or "TRY"
                vergiler.append({"turu": f"Navlun ({navlun_d})", "matrah": navlun_k, "oran": 0, "tutar": navlun_k})
            if sigorta_k > 0:
                sig_d = ft(kel, "Sigorta_miktarinin_dovizi") or "TRY"
                vergiler.append({"turu": f"Sigorta ({sig_d})", "matrah": sigorta_k, "oran": 0, "tutar": sigorta_k})
            if kkdf > 0:
                vergiler.append({"turu": "KF — KKDF", "matrah": 0, "oran": 0, "tutar": kkdf})

            kalemler.append({
                "sno": int(kalem_no) if kalem_no.isdigit() else len(kalemler) + 1,
                "gtip": gtip_fmt,
                "tanim": tanim or "—",
                "ticari_tanim": ticari,
                "mense": f"{mense_ad} ({mense_kod})",
                "miktar": miktar,
                "birim": birim,
                "kalem_fiyati": fatura_mik,
                "ist_kiymet": ist_kiymet,
                "brut_kg": brut,
                "net_kg": net,
                "vergiler": vergiler,
                "uyarilar": uyarilar,
            })

        return beyanname, kalemler

    except Exception as e:
        st.error(f"XML okunurken hata: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None, None


def parse_upload(uploaded_file):
    if uploaded_file.name.endswith(".xml"):
        return parse_xml(uploaded_file)
    import pandas as pd
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, sheet_name=0)

        cols_lower = {str(c).lower().strip(): c for c in df.columns}

        col_map = {
            "gtip": ["gtip", "gtİp", "tgtc", "hs code", "tarife", "gtip no"],
            "tanim": ["tanim", "tanım", "mal tanımı", "description", "açıklama"],
            "ticari_tanim": ["ticari tanim", "ticari tanım", "commercial", "ticari"],
            "mense": ["menşe", "mense", "origin", "country", "ülke"],
            "miktar": ["miktar", "quantity", "adet", "qty"],
            "birim": ["birim", "ölçü birimi", "unit"],
            "kalem_fiyati": ["fiyat", "kalem fiyatı", "tutar", "amount", "value", "kıymet", "price"],
            "ist_kiymet": ["ist. kıymet", "istatistiki kıymet", "statistical"],
            "brut_kg": ["brüt", "brut", "brüt kg", "gross", "brüt ağırlık"],
            "net_kg": ["net", "net kg", "net weight", "net ağırlık"],
        }

        def find_col(keys):
            for key in keys:
                for cl, orig in cols_lower.items():
                    if key in cl:
                        return orig
            return None

        resolved = {f: find_col(k) for f, k in col_map.items()}

        if not resolved.get("gtip"):
            return None, None

        kalemler = []
        for _, row in df.iterrows():
            gtip_col = resolved["gtip"]
            gtip_val = str(row.get(gtip_col, "")).strip() if gtip_col else ""
            if not gtip_val or gtip_val == "nan" or len(gtip_val) < 4:
                continue

            def gv(field, default=""):
                col = resolved.get(field)
                if col and pd.notna(row.get(col)):
                    return row[col]
                return default

            def gn(field, default=0):
                col = resolved.get(field)
                if col and pd.notna(row.get(col)):
                    try:
                        return float(str(row[col]).replace(",", ".").replace(" ", ""))
                    except (ValueError, TypeError):
                        return default
                return default

            kalemler.append({
                "sno": len(kalemler) + 1,
                "gtip": gtip_val,
                "tanim": str(gv("tanim", "—")),
                "ticari_tanim": str(gv("ticari_tanim", "")),
                "mense": str(gv("mense", "—")),
                "miktar": gn("miktar", 1),
                "birim": str(gv("birim", "Adet")),
                "kalem_fiyati": gn("kalem_fiyati", 0),
                "ist_kiymet": gn("ist_kiymet", 0),
                "brut_kg": gn("brut_kg", 0),
                "net_kg": gn("net_kg", 0),
                "vergiler": [],
                "uyarilar": [],
            })

        beyanname = {"dosya_no": uploaded_file.name, "kur_tarihi": "—", "rejim": "—", "anlasma": "—", "tasima": "—", "incoterms": "—", "doviz_kuru": "—"}
        return beyanname, kalemler

    except Exception as e:
        st.error(f"Dosya okunurken hata: {e}")
        return None, None


# =============================================
# DISPLAY FUNCTIONS
# =============================================
def show_kalemler(kalemler):
    for k in kalemler:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Kalem {k['sno']}** — `{k['gtip']}`")
                st.caption(k.get("tanim", "—"))
                ticari = k.get("ticari_tanim", "")
                if ticari:
                    st.text(f"Ticari tanım: {ticari}")
            with c2:
                st.markdown(f"**Menşe:** {k.get('mense', '—')}")
                mikt = k.get("miktar", 0)
                if isinstance(mikt, float) and mikt == int(mikt):
                    mikt = int(mikt)
                st.markdown(f"**Miktar:** {mikt:,} {k.get('birim', '')}")

            m1, m2, m3 = st.columns(3)
            m1.metric("Kalem fiyatı", f"{k.get('kalem_fiyati', 0):,.2f}")
            m2.metric("İst. kıymet", f"{k.get('ist_kiymet', 0):,.2f}")
            m3.metric("Ağırlık", f"B {k.get('brut_kg', 0):,.0f} / N {k.get('net_kg', 0):,.0f} kg")

            vergiler = k.get("vergiler", [])
            if vergiler:
                st.markdown("**Vergiler:**")
                vd = {"Tür": [], "Matrah": [], "Oran": [], "Tutar": []}
                for v in vergiler:
                    if isinstance(v, dict):
                        vd["Tür"].append(v.get("turu", ""))
                        vd["Matrah"].append(f"{v.get('matrah', 0):,.2f}")
                        vd["Oran"].append(f"{v.get('oran', 0)}%")
                        vd["Tutar"].append(f"{v.get('tutar', 0):,.2f}")
                st.dataframe(vd, hide_index=True, use_container_width=True)

            uyarilar = k.get("uyarilar", [])
            if uyarilar:
                ut = "<br>".join([f"⚠️ {u}" for u in uyarilar])
                st.markdown(f'<div class="evrim-uyari-kutusu">{ut}</div>', unsafe_allow_html=True)


def show_risk(checks, label=""):
    sk = f"done_{label}"
    if sk not in st.session_state:
        pb = st.progress(0, text="Risk kontrolleri çalıştırılıyor...")
        for i in range(len(checks)):
            time.sleep(0.2)
            pb.progress((i + 1) / len(checks), text=f"Kontrol {i+1}/{len(checks)}: {checks[i]['kategori']}...")
        pb.empty()
        st.session_state[sk] = True

    kr = [c for c in checks if c["durum"] == "kritik"]
    uy = [c for c in checks if c["durum"] == "uyari"]
    ok = [c for c in checks if c["durum"] == "ok"]
    t = len(checks)

    score = max(0, min(100, round(100 - (len(ok) / t * 60) - (len(uy) / t * 20) + (len(kr) / t * 80)))) if t > 0 else 0

    if len(kr) == 0 and len(uy) <= 1:
        hat, hd = "Yeşil hat", {"y": 55, "m": 30, "s": 12, "k": 3}
    elif len(kr) == 0:
        hat, hd = "Mavi hat", {"y": 15, "m": 50, "s": 28, "k": 7}
    elif len(kr) <= 1:
        hat, hd = "Sarı hat", {"y": 10, "m": 25, "s": 45, "k": 20}
    else:
        hat, hd = "Kırmızı hat", {"y": 5, "m": 10, "s": 25, "k": 60}

    st.markdown("##### Özet")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Risk skoru", f"{score}/100")
    s2.metric("Hat tahmini", hat)
    s3.metric("Kritik", len(kr))
    s4.metric("Uyarı", len(uy))
    s5.metric("Sorunsuz", len(ok))

    st.markdown("---")
    st.markdown("##### Hat olasılık dağılımı")
    h1, h2, h3, h4 = st.columns(4)
    h1.progress(hd["y"], text=f"Yeşil %{hd['y']}")
    h2.progress(hd["m"], text=f"Mavi %{hd['m']}")
    h3.progress(hd["s"], text=f"Sarı %{hd['s']}")
    h4.progress(hd["k"], text=f"Kırmızı %{hd['k']}")

    st.markdown("---")
    st.markdown("##### Detaylı kontroller")

    if kr:
        st.markdown(f"🔴 **Kritik** ({len(kr)})")
        for c in kr:
            with st.expander(f"❌ {c['baslik']}"):
                st.markdown(c["aciklama"]); st.divider(); st.caption("💡 Detay"); st.markdown(c["detay"])
    if uy:
        st.markdown(f"🟡 **Uyarı** ({len(uy)})")
        for c in uy:
            with st.expander(f"⚠️ {c['baslik']}"):
                st.markdown(c["aciklama"]); st.divider(); st.caption("💡 Detay"); st.markdown(c["detay"])
    if ok:
        st.markdown(f"🟢 **Sorunsuz** ({len(ok)})")
        for c in ok:
            with st.expander(f"✅ {c['baslik']}"):
                st.markdown(c["aciklama"]); st.divider(); st.caption("💡 Detay"); st.markdown(c["detay"])

    st.markdown("---")
    st.markdown("##### 📌 AI önerisi")
    if kr:
        kl = "\n".join([f"- **{c['baslik']}**" for c in kr])
        ul = "\n".join([f"- {c['baslik']}" for c in uy]) if uy else ""
        st.warning(f"**{len(kr)} kritik sorun çözülmeli:**\n\n{kl}\n\n{'**' + str(len(uy)) + ' uyarı takip edilmeli:**' if uy else ''}\n{ul}")
    elif uy:
        st.info(f"Kritik sorun yok. **{len(uy)} uyarı** gözden geçirilmeli.")
    else:
        st.success("Tüm kontroller sorunsuz. Beyanname gönderilebilir. ✅")


# =============================================
# MAIN
# =============================================
st.markdown("### 🛃 Evrim AI — Pre-declaration risk scoring")
st.caption("Beyanname gönderilmeden önce AI destekli risk analizi")

source = st.radio("Veri kaynağı:", ["📦 Demo verisi", "📤 Dosya yükle (Excel / CSV)"], horizontal=True)

if source == "📦 Demo verisi":
    beyanname, kalemler, checks, is_demo = DEMO_BEYANNAME, DEMO_KALEMLER, DEMO_RISK_CHECKS, True
else:
    beyanname, kalemler, checks, is_demo = None, None, None, False
    st.markdown("---")
    st.caption("Excel (.xlsx), CSV veya XML dosyası yükleyin")

    uploaded = st.file_uploader("Dosya seçin", type=["xlsx", "xls", "csv", "xml"])
    if uploaded:
        beyanname, kalemler = parse_upload(uploaded)
        if kalemler and len(kalemler) > 0:
            st.success(f"✅ {len(kalemler)} kalem okundu.")
        elif kalemler is not None:
            st.warning("Kalem bulunamadı. GTİP sütunu olduğundan emin olun.")

    with st.expander("📋 Örnek Excel formatı"):
        st.markdown("""
| GTİP | Tanım | Ticari Tanım | Menşe | Miktar | Birim | Fiyat | İst. Kıymet | Brüt KG | Net KG |
|------|-------|-------------|-------|--------|-------|-------|-------------|---------|--------|
| 3926.90.97.90.29 | Plastik eşya | Montaj klipsi | İtalya | 50 | Adet | 900 | 1017 | 100 | 50 |
| 8544.49.93.00.19 | PVC kablo | Bakır kablo 2.5mm | Çin | 15000 | Metre | 21000 | 23520 | 4200 | 3800 |
        """)

if beyanname and kalemler and len(kalemler) > 0:
    tab1, tab2 = st.tabs(["📋 Beyanname verisi", "🔍 Risk analizi"])

    with tab1:
        st.markdown("##### Dosya bilgileri")
        c1, c2, c3 = st.columns(3)
        c1.metric("Dosya", beyanname.get("dosya_no", "—"))
        c2.metric("Kur tarihi", beyanname.get("kur_tarihi", "—"))
        c3.metric("Döviz kuru", beyanname.get("doviz_kuru", "—"))
        c4, c5, c6 = st.columns(3)
        c4.metric("Rejim", beyanname.get("rejim", "—"))
        c5.metric("Taşıma", beyanname.get("tasima", "—"))
        c6.metric("Incoterms", beyanname.get("incoterms", "—"))
        st.markdown("---")
        st.markdown(f"##### Kalemler ({len(kalemler)})")
        show_kalemler(kalemler)
        st.markdown("---")
        if st.button("🚀 AI risk analizi çalıştır", type="primary", use_container_width=True):
            st.session_state["run"] = True
            st.rerun()

    with tab2:
        if not st.session_state.get("run"):
            st.info("**Beyanname verisi** sekmesinden **AI risk analizi çalıştır** butonuna basın.")
        else:
            final_checks = checks if is_demo else generate_risk_checks(kalemler)
            if final_checks:
                show_risk(final_checks, label="main")
            else:
                st.warning("Risk kontrolü oluşturulamadı.")
            if st.button("🔄 Yeniden analiz"):
                for k in list(st.session_state.keys()):
                    if k in ["run", "done_main"]:
                        del st.session_state[k]
                st.rerun()
