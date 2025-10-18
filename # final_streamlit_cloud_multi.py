import streamlit as st
import re
import csv
import io
import requests
import time

# === 1. Konfigurasi halaman ===
st.set_page_config(page_title="Pencarian & Klasifikasi OPTK A1/A2 by Noya", layout="wide")

st.title("🔎 Pencarian & Klasifikasi OPTK A1 / A2 Berdasarkan Inang / Daerah / Media")
st.markdown("**Enhanced with GBIF Taxonomy • by Noya & ChatGPT**")
st.markdown("---")

# === 2. Pilihan jenis OPTK ===
jenis_optk = st.selectbox("Pilih jenis OPTK:", ["A1", "A2"], index=1)
file_map = {"A1": "teks_OPTKA1.txt", "A2": "teks_OPTKA2.txt"}
file_terpilih = file_map[jenis_optk]

# === 3. Baca file ===
try:
    with open(file_terpilih, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
except FileNotFoundError:
    st.error(f"File '{file_terpilih}' tidak ditemukan! Pastikan file ada di folder yang sama.")
    st.stop()

# === 4. Gabungkan baris jadi record ===
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

st.write(f"📂 Jumlah record dalam {jenis_optk}: {len(records)}")
st.markdown("---")

# === 5. Input pencarian ===
st.subheader("Masukkan kata pencarian")
kata_inang = st.text_input("🪴 Inang / Host (pisahkan koma jika lebih dari satu)")
kata_daerah = st.text_input("📍 Daerah Sebar (pisahkan koma jika lebih dari satu)")
kata_media = st.text_input("📦 Media Pembawa / Pathway (pisahkan koma jika lebih dari satu)")

# === Fungsi bantu regex ===
def buat_regex_multi(kata_input):
    if kata_input:
        kata_list = [k.strip() for k in kata_input.split(",") if k.strip()]
        return [re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE) for k in kata_list]
    return []

# === Fungsi deteksi kategori lokal (regex) ===
kategori_optk = {
    "Serangga": [
        "Coleoptera", "Lepidoptera", "Diptera", "Hemiptera", "Hymenoptera",
        "Insecta", "beetle", "weevil", "borer", "bug", "hopper", "moth", "fly", "thrips"
    ],
    "Virus": ["virus", "viroid", "begomovirus", "tospovirus", "potyvirus", "mosaic"],
    "Bakteri": ["bacterium", "bacteria", "Ralstonia", "Xanthomonas", "Erwinia", "Pseudomonas"],
    "Jamur": ["Fusarium", "Phytophthora", "Cercospora", "Colletotrichum", "Rhizoctonia"],
    "Nematoda": ["Meloidogyne", "Heterodera", "Globodera", "Pratylenchus", "Radopholus"],
    "Tungau": ["Acarina", "Tetranychus", "mite", "Brevipalpus"],
    "Gulma": ["weed", "Amaranthus", "Avena", "Eichhornia", "Imperata", "Mikania"],
    "Siput": ["Achatina", "snail", "slug", "Pomacea"],
    "Fitoplasma": ["phytoplasma", "mycoplasma", "spiroplasma"]
}

def deteksi_kategori_lokal(teks):
    for kategori, kata_list in kategori_optk.items():
        for kata in kata_list:
            if re.search(rf"\b{kata}\b", teks, re.IGNORECASE):
                return kategori
    return "Tidak Terklasifikasi"

def deteksi_kategori_gbif(nama):
    try:
        url = f"https://api.gbif.org/v1/species?name={nama}"
        r = requests.get(url, timeout=10)
        data = r.json()

        if "results" in data and len(data["results"]) > 0:
            hasil = data["results"][0]
            kingdom = hasil.get("kingdom", "").lower()
            kelas = hasil.get("class", "").lower()
            phylum = hasil.get("phylum", "").lower()
            canonical = hasil.get("canonicalName", "").lower()

            # --- PERBAIKAN UNTUK PHYTOSPLASMA DAN BAKTERI LAIN ---
            if "phytoplasma" in canonical:
                return "Bakteri"
            if "bacteria" in kingdom:
                return "Bakteri"
            elif "virus" in kingdom:
                return "Virus"
            elif "fungi" in kingdom:
                return "Jamur"
            elif "animalia" in kingdom:
                if "insecta" in kelas:
                    return "Serangga"
                elif "arachnida" in kelas:
                    return "Tungau"
                elif "nematoda" in phylum:
                    return "Nematoda"
                else:
                    return "Hewan Lain"
            elif "plantae" in kingdom:
                return "Tumbuhan"
            else:
                return "Tidak Terklasifikasi"
        else:
            return "Nama Tidak Ditemukan"
    except Exception as e:
        return f"Error: {e}"

# === 6. Tombol cari ===
if st.button("🔍 Jalankan Pencarian"):
    pattern_inang_list = buat_regex_multi(kata_inang)
    pattern_daerah_list = buat_regex_multi(kata_daerah)
    pattern_media_list = buat_regex_multi(kata_media)

    hasil = []
    for rec in records:
        def cocok(pattern_list):
            if not pattern_list:
                return True
            return any(p.search(rec) for p in pattern_list)
        if cocok(pattern_inang_list) and cocok(pattern_daerah_list) and cocok(pattern_media_list):
            hasil.append(rec)

    if hasil:
        st.success(f"Ditemukan {len(hasil)} record dalam OPTK {jenis_optk}. Memproses klasifikasi...")

        hasil_per_kategori = {}
        data_csv = []

        progress = st.progress(0)
        total = len(hasil)

        for i, h in enumerate(hasil, start=1):
            kata_split = h.split()
            target = " ".join(kata_split[:3])
            gbif_kategori = deteksi_kategori_gbif(target)
            kategori = gbif_kategori if gbif_kategori else deteksi_kategori_lokal(h)

            hasil_per_kategori.setdefault(kategori, []).append(h)

            h_clean = re.sub(r"^\d+\.\s*", "", h)
            h_clean = re.sub(r"--- Halaman \d+ ---", "", h_clean)
            h_clean = re.sub(r"Dokumen ini telah ditandatangani.*", "", h_clean)
            h_clean = h_clean.strip()

            host = re.search(r"[Hh]ost[:：]\s*([^;]*)", h)
            pathway = re.search(r"[Pp]athway[:：]\s*([^;]*)", h)
            dist = re.search(r"[Dd]istribution[:：]\s*([^;]*)", h)
            google_link = f"https://www.google.com/search?q={target.replace(' ', '+')}"

            data_csv.append({
                "No": i,
                "Target": target,
                "Kategori": kategori,
                "Host": host.group(1).strip() if host else "-",
                "Pathway": pathway.group(1).strip() if pathway else "-",
                "Distribution": dist.group(1).strip() if dist else "-",
                "Link Google": google_link
            })

            progress.progress(i / total)
            time.sleep(0.5)

        # === Tampilkan hasil ===
        for kategori, daftar in hasil_per_kategori.items():
            st.markdown(f"### 🧬 {kategori} ({len(daftar)} hasil)")
            for teks in daftar:
                target = " ".join(teks.split()[:3])
                link = f"https://www.google.com/search?q={target.replace(' ', '+')}"
                st.markdown(f"- [{target}]({link})", unsafe_allow_html=True)
            st.markdown("---")

        # === Download CSV ===
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["No", "Target", "Kategori", "Host", "Pathway", "Distribution", "Link Google"])
        writer.writeheader()
        writer.writerows(data_csv)

        st.download_button(
            label=f"💾 Download Hasil OPTK {jenis_optk} (CSV)",
            data=output.getvalue(),
            file_name=f"hasil_OPTKA{jenis_optk}_GBIF.csv",
            mime="text/csv"
        )
    else:
        st.warning("Tidak ditemukan hasil yang cocok.")

