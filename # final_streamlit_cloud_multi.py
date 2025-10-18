# final_streamlit_optk_duatab.py
import streamlit as st
import re
import csv
import io

# === 1. Konfigurasi halaman ===
st.set_page_config(page_title="Pencarian & Target OPTK A1/A2 by Noya", layout="wide")

st.title("🦋 Sistem Pencarian & Analisis Target OPTK A1 / A2")
st.markdown("**by: Noya**")
st.markdown("---")

# === Tabs utama ===
tab1, tab2 = st.tabs(["🔍 Pencarian OPTK", "🎯 Analisis Target OPTK"])

# === Pilihan jenis OPTK ===
jenis_optk = st.selectbox("Pilih jenis OPTK:", ["A1", "A2"], index=1)
file_map = {"A1": "teks_OPTKA1.txt", "A2": "teks_OPTKA2.txt"}
file_terpilih = file_map[jenis_optk]

# === Baca file OPTK ===
try:
    with open(file_terpilih, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
except FileNotFoundError:
    st.error(f"File '{file_terpilih}' tidak ditemukan!")
    st.stop()

# === Gabungkan baris jadi record ===
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

# === Fungsi kategori ===
def get_kategori_map(jenis_optk):
    if jenis_optk == "A1":
        return {
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
    else:
        return {
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

kategori_map = get_kategori_map(jenis_optk)

def kategori_by_index(index):
    no = index + 2
    for kategori, (start, end) in kategori_map.items():
        if start <= no <= end:
            return kategori
    return "Tidak Terklasifikasi"

# === Fungsi bantu ===
def buat_regex_multi(kata_input):
    if kata_input:
        kata_list = [k.strip() for k in kata_input.split(",") if k.strip()]
        return [re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE) for k in kata_list]
    return []

def cocok(pattern_list, teks):
    if not pattern_list:
        return True
    return any(p.search(teks) for p in pattern_list)

# ==========================================================
# === TAB 1: Pencarian OPTK (TIDAK DIUBAH)
# ==========================================================
with tab1:
    st.subheader("Masukkan kata pencarian")
    kata_inang = st.text_input("🪴 Inang / Host (pisahkan koma jika lebih dari satu)")
    kata_daerah = st.text_input("📍 Daerah Sebar (pisahkan koma jika lebih dari satu)")
    kata_media = st.text_input("📦 Media Pembawa / Pathway (pisahkan koma jika lebih dari satu)")

    if st.button("🔍 Cari", key="cari_optk"):
        pattern_inang = buat_regex_multi(kata_inang)
        pattern_daerah = buat_regex_multi(kata_daerah)
        pattern_media = buat_regex_multi(kata_media)

        hasil = []
        for rec in records:
            if cocok(pattern_inang, rec) and cocok(pattern_daerah, rec) and cocok(pattern_media, rec):
                hasil.append(rec)

        if hasil:
            st.success(f"Ditemukan {len(hasil)} record pada OPTK {jenis_optk}.")
            hasil_per_kategori = {}
            data_csv = []

            for i, h in enumerate(hasil, start=1):
                kategori = kategori_by_index(records.index(h))
                hasil_per_kategori.setdefault(kategori, []).append(h)

                h_clean = re.sub(r"^\d+\.\s*", "", h).strip()
                kata_split = h_clean.split()
                target = " ".join(kata_split[:3])
                google_link = f"https://www.google.com/search?q={target.replace(' ', '+')}"

                host = re.search(r"[Hh]ost[:：]\s*([^;]*)", h)
                pathway = re.search(r"[Pp]athway[:：]\s*([^;]*)", h)
                dist = re.search(r"[Dd]istribution[:：]\s*([^;]*)", h)

                data_csv.append({
                    "No": i,
                    "Target": target,
                    "Kategori": kategori,
                    "Host": host.group(1).strip() if host else "-",
                    "Pathway": pathway.group(1).strip() if pathway else "-",
                    "Distribution": dist.group(1).strip() if dist else "-",
                    "Google": google_link
                })

            for kategori, daftar in hasil_per_kategori.items():
                st.markdown(f"### 🧬 {kategori} ({len(daftar)} hasil)")
                for teks in daftar:
                    kata_split = teks.split()
                    target = " ".join(kata_split[:3])
                    link = f"https://www.google.com/search?q={target.replace(' ', '+')}"
                    st.markdown(f"- [{target}]({link})", unsafe_allow_html=True)
                st.markdown("---")

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["No", "Target", "Kategori", "Host", "Pathway", "Distribution", "Google"])
            writer.writeheader()
            writer.writerows(data_csv)

            st.download_button(
                label=f"💾 Download Hasil OPTK {jenis_optk} (CSV)",
                data=output.getvalue(),
                file_name=f"hasil_OPTKA{jenis_optk}_grup.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"Tidak ditemukan hasil yang cocok pada OPTK {jenis_optk}.")

# ==========================================================
# === TAB 2: Analisis Target OPTK (DENGAN PENGELOMPOKAN)
# ==========================================================
with tab2:
    st.subheader("Analisis Target OPTK Berdasarkan Asal & Tujuan")

    inang_asal = st.text_input("🪴 Inang / Host (pisahkan koma jika lebih dari satu)", key="asal_inang")
    daerah_asal = st.text_input("📍 Daerah Sebar Asal", key="asal_daerah")
    daerah_tujuan = st.text_input("📍 Daerah Sebar Tujuan", key="tujuan_daerah")
    media_asal = st.text_input("📦 Media Pembawa (opsional)", key="asal_media")

    if st.button("🎯 Analisis Target", key="analisis_target"):
        pattern_inang = buat_regex_multi(inang_asal)
        pattern_media = buat_regex_multi(media_asal)
        pattern_asal = buat_regex_multi(daerah_asal)
        pattern_tujuan = buat_regex_multi(daerah_tujuan)

        hasil_asal = [r for r in records if cocok(pattern_inang, r) and cocok(pattern_media, r) and cocok(pattern_asal, r)]
        hasil_tujuan = [r for r in records if cocok(pattern_inang, r) and cocok(pattern_media, r) and cocok(pattern_tujuan, r)]

        if not hasil_asal:
            st.warning("❗ Tidak ditemukan data untuk daerah asal.")
        else:
            target_optk = []
            for r in hasil_asal:
                kategori = kategori_by_index(records.index(r))
                nama = " ".join(re.sub(r"^\d+\.\s*", "", r).split()[:3])
                if not any(nama.lower() in t.lower() for t in hasil_tujuan):
                    target_optk.append((nama, kategori))

            if target_optk:
                hasil_per_kategori = {}
                for nama, kategori in target_optk:
                    hasil_per_kategori.setdefault(kategori, []).append(nama)

                st.success("🎯 Ditemukan Target OPTK yang Berbeda:")
                for kategori, daftar in hasil_per_kategori.items():
                    st.markdown(f"### 🧬 {kategori} ({len(daftar)} target)")
                    for n in daftar:
                        link = f"https://www.google.com/search?q={n.replace(' ', '+')}"
                        st.markdown(f"- [{n}]({link})", unsafe_allow_html=True)
                    st.markdown("---")
            else:
                st.info("✅ Tidak ada target. Daerah asal dan tujuan memiliki OPTK yang sama.")
