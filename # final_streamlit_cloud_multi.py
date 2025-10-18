# === final_optk_dual_tab_by_noya.py ===
import streamlit as st
import re
import csv
import io

# === 1. Konfigurasi halaman ===
st.set_page_config(page_title="Pencarian & Target OPTK A1/A2 by Noya", layout="wide")

st.title("🌿 Sistem Pencarian & Analisis Target OPTK A1/A2")
st.markdown("**by: Noya**")
st.markdown("---")

# === Tabs ===
tab1, tab2 = st.tabs(["🔍 Pencarian OPTK", "🎯 Target OPTK"])

# === Pemetaan kategori per rentang baris ===
kategori_map_A1 = {
    "Serangga": (2, 237),
    "Tungau": (239, 262),
    "Keong": (264, 278),
    "Siput": (280, 293),
    "Nematoda": (295, 360),
    "Gulma parasitik": (362, 392),
    "Gulma non parasitik": (398, 405),
    "Cendawan": (406, 538),
    "Bakteri": (540, 594),
    "Mollicute": (596, 610),
    "Virus": (612, 732),
    "Viroid": (733, 739)
}
kategori_map_A2 = {
    "Serangga": (2, 50),
    "Tungau": (52, 58),
    "Keong": (60, 61),
    "Nematoda": (63, 72),
    "Gulma non parasitik": (74, 77),
    "Cendawan": (79, 108),
    "Bakteri": (110, 123),
    "Virus": (125, 136),
    "Viroid": (138, 138)
}

# === Fungsi bantu umum ===
def baca_file_optk(jenis):
    file_map = {"A1": "teks_OPTKA1.txt", "A2": "teks_OPTKA2.txt"}
    file_terpilih = file_map[jenis]
    try:
        with open(file_terpilih, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        st.error(f"File '{file_terpilih}' tidak ditemukan! Pastikan file ada di folder yang sama.")
        st.stop()

    records = []
    temp = ""
    for line in lines:
        line = line.strip()
        if re.match(r"^\d+\.", line):
            if temp:
                records.append(temp)
            temp = line
        else:
            temp += " " + line
    if temp:
        records.append(temp)
    return records

def kategori_by_index(index, jenis):
    if jenis == "A1":
        kategori_map = kategori_map_A1
    else:
        kategori_map = kategori_map_A2
    no = index + 2
    for kategori, (start, end) in kategori_map.items():
        if start <= no <= end:
            return kategori
    return "Tidak Terklasifikasi"

def buat_regex_multi(kata_input):
    if kata_input:
        kata_list = [k.strip() for k in kata_input.split(",") if k.strip()]
        return [re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE) for k in kata_list]
    return []

def cocok(pattern_list, teks):
    if not pattern_list:
        return True
    return any(p.search(teks) for p in pattern_list)

# ============================================================
# === TAB 1: PENCARIAN OPTK
# ============================================================
with tab1:
    jenis_optk = st.selectbox("Pilih jenis OPTK:", ["A1", "A2"], index=1, key="optk_search")
    records = baca_file_optk(jenis_optk)
    st.write(f"📂 Jumlah record dalam {jenis_optk}: {len(records)}")
    st.markdown("---")

    kata_inang = st.text_input("🪴 Inang / Host (pisahkan koma jika lebih dari satu)")
    kata_daerah = st.text_input("📍 Daerah Sebar (pisahkan koma jika lebih dari satu)")
    kata_media = st.text_input("📦 Media Pembawa / Pathway (opsional)")

    if st.button("🔍 Cari", key="cari_optk"):
        pattern_inang = buat_regex_multi(kata_inang)
        pattern_daerah = buat_regex_multi(kata_daerah)
        pattern_media = buat_regex_multi(kata_media)

        hasil = [
            rec for rec in records
            if cocok(pattern_inang, rec) and cocok(pattern_daerah, rec) and cocok(pattern_media, rec)
        ]

        if hasil:
            st.success(f"Ditemukan {len(hasil)} record pada OPTK {jenis_optk}.")
            hasil_per_kategori = {}
            for rec in hasil:
                kategori = kategori_by_index(records.index(rec), jenis_optk)
                hasil_per_kategori.setdefault(kategori, []).append(rec)

            for kategori, daftar in hasil_per_kategori.items():
                st.markdown(f"### 🧬 {kategori} ({len(daftar)} hasil)")
                for teks in daftar:
                    target = " ".join(re.sub(r"^\d+\.\s*", "", teks).split()[:3])
                    link = f"https://www.google.com/search?q={target.replace(' ', '+')}"
                    st.markdown(f"- [{target}]({link})", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.warning(f"Tidak ditemukan hasil pada OPTK {jenis_optk}.")

# ============================================================
# === TAB 2: TARGET OPTK
# ============================================================
with tab2:
    jenis_optk2 = st.selectbox("Pilih jenis OPTK:", ["A1", "A2"], index=1, key="optk_target")
    records2 = baca_file_optk(jenis_optk2)

    st.subheader("Masukkan Data Analisis Target")
    inang = st.text_input("🪴 Inang / Host (wajib)", key="host_target")
    daerah_asal = st.text_input("📍 Daerah Sebar Asal (wajib)", key="asal_target")
    daerah_tujuan = st.text_input("📍 Daerah Sebar Tujuan (wajib)", key="tujuan_target")
    media = st.text_input("📦 Media Pembawa / Pathway (opsional)", key="media_target")

    if st.button("🎯 Analisis Target", key="analisis_target"):
        if not inang or not daerah_asal or not daerah_tujuan:
            st.error("⚠️ Harap isi Inang, Daerah Asal, dan Daerah Tujuan.")
            st.stop()

        pattern_inang = buat_regex_multi(inang)
        pattern_media = buat_regex_multi(media)

        hasil_asal = [
            r for r in records2
            if cocok(pattern_inang, r) and cocok(pattern_media, r) and re.search(daerah_asal, r, re.IGNORECASE)
        ]
        hasil_tujuan = [
            r for r in records2
            if cocok(pattern_inang, r) and cocok(pattern_media, r) and re.search(daerah_tujuan, r, re.IGNORECASE)
        ]

        if not hasil_asal:
            st.warning("Tidak ditemukan OPTK di daerah asal berdasarkan inang yang dimasukkan.")
        else:
            optk_asal = { " ".join(re.sub(r"^\d+\.\s*", "", h).split()[:3]) for h in hasil_asal }
            optk_tujuan = { " ".join(re.sub(r"^\d+\.\s*", "", h).split()[:3]) for h in hasil_tujuan }

            target_optk = optk_asal - optk_tujuan  # beda dari tujuan
            if target_optk:
                st.success(f"🎯 Ditemukan {len(target_optk)} target OPTK potensial:")
                for t in sorted(target_optk):
                    idx = next((i for i, r in enumerate(records2) if t in r), None)
                    kategori = kategori_by_index(idx, jenis_optk2) if idx is not None else "-"
                    st.markdown(f"- **{t}** ({kategori})")
            else:
                st.info("✅ Tidak ada target. Semua OPTK dari daerah asal juga ditemukan di daerah tujuan.")
