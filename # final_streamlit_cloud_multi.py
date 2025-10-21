import streamlit as st
import pandas as pd
import csv
import io
import re

# =========================================
# === Fungsi bantu
# =========================================
def buat_regex_multi(teks):
    """Membuat pola regex dari input teks yang dipisahkan koma"""
    if not teks:
        return None
    pola = "|".join([re.escape(t.strip()) for t in teks.split(",") if t.strip()])
    return pola if pola else None

def cocok(pola, teks):
    """Cek apakah pola cocok dengan teks"""
    if not pola:
        return True
    return re.search(pola, teks, re.IGNORECASE)

def kategori_by_index(i):
    """Menentukan kategori berdasarkan indeks baris"""
    if 2 <= i <= 237: return "Serangga"
    if 239 <= i <= 262: return "Tungau"
    if 264 <= i <= 278: return "Keong"
    if 280 <= i <= 293: return "Siput"
    if 295 <= i <= 360: return "Nematoda"
    if 362 <= i <= 392: return "Gulma Parasitik"
    if 398 <= i <= 404: return "Gulma Non Parasitik"
    if 406 <= i <= 538: return "Cendawan"
    if 540 <= i <= 594: return "Bakteri"
    if 596 <= i <= 610: return "Mollicute"
    if 612 <= i <= 737: return "Virus"
    return "Lainnya"

# =========================================
# === Simulasi data record (ganti dengan data aslimu)
# =========================================
records = [
    "1. Bactrocera dorsalis\tMangifera indica\tBuah\tSumatera, Kalimantan",
    "2. Fusarium oxysporum\tElaeis guineensis\tTanah\tRiau, Jambi",
    "3. Meloidogyne incognita\tSolanum lycopersicum\tAkar\tJawa Barat",
    "4. Rhynchophorus ferrugineus\tCocos nucifera\tBatang\tKalimantan Selatan",
]

# =========================================
# === Tampilan Aplikasi Streamlit
# =========================================
st.set_page_config(page_title="Analisis Data OPTK", layout="wide")
st.title("🌿 Sistem Analisis dan Pencarian Data OPTK")

tab1, tab2, tab3 = st.tabs([
    "📋 Pencarian Berdasarkan Inang / Media",
    "🎯 Analisis Target OPTK",
    "🔍 Pencarian Berdasarkan Nama OPTK"
])

# ==========================================================
# === TAB 1: Pencarian Berdasarkan Inang / Media
# ==========================================================
with tab1:
    st.subheader("Cari OPTK Berdasarkan Inang dan Media Pembawa")

    inang = st.text_input("🪴 Inang / Host", key="inang")
    media = st.text_input("📦 Media Pembawa (opsional)", key="media")

    if st.button("🔍 Cari OPTK", key="cari_optk"):
        pattern_inang = buat_regex_multi(inang)
        pattern_media = buat_regex_multi(media)
        hasil = [r for r in records if cocok(pattern_inang, r) and cocok(pattern_media, r)]

        if hasil:
            st.success(f"✅ Ditemukan {len(hasil)} hasil cocok.")
            data_csv = []
            for i, teks in enumerate(hasil, 1):
                kata_split = re.sub(r"^\d+\.\s*", "", teks).split("\t")
                target = " ".join(kata_split[0].split()[:3])
                kategori = kategori_by_index(records.index(teks))
                host = kata_split[1] if len(kata_split) > 1 else "-"
                media_pembawa = kata_split[2] if len(kata_split) > 2 else "-"
                distribusi = kata_split[3] if len(kata_split) > 3 else "-"
                link = f"https://www.google.com/search?q={target.replace(' ', '+')}"

                data_csv.append({
                    "No": i,
                    "Target": target,
                    "Kategori": kategori,
                    "Host": host,
                    "Pathway": media_pembawa,
                    "Distribution": distribusi,
                    "Google": link
                })

                st.markdown(f"- [{target}]({link})", unsafe_allow_html=True)

            st.markdown("---")
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["No", "Target", "Kategori", "Host", "Pathway", "Distribution", "Google"])
            writer.writeheader()
            writer.writerows(data_csv)

            st.download_button(
                label="💾 Download Hasil (CSV)",
                data=output.getvalue(),
                file_name="hasil_pencarian_optk.csv",
                mime="text/csv"
            )
        else:
            st.warning("❗ Tidak ditemukan hasil yang cocok.")


# ==========================================================
# === TAB 2: Analisis Target OPTK (Asal vs Tujuan)
# ==========================================================
with tab2:
    st.subheader("Analisis Target OPTK Berdasarkan Asal & Tujuan")

    inang_asal = st.text_input("🪴 Inang / Host", key="asal_inang")
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


# ==========================================================
# === TAB 3: Pencarian Inang & Daerah Sebar Berdasarkan OPTK
# ==========================================================
with tab3:
    st.subheader("Cari Inang dan Daerah Sebar Berdasarkan Nama OPTK")

    optk_input = st.text_input("🧬 Masukkan Nama OPTK (bisa lebih dari satu, pisahkan koma)", key="cari_optk3")

    if st.button("🔎 Cari Data OPTK", key="cari_optk_btn"):
        if optk_input.strip():
            pattern_optk = buat_regex_multi(optk_input)
            hasil_cari = [r for r in records if cocok(pattern_optk, r)]

            if hasil_cari:
                st.success(f"✅ Ditemukan {len(hasil_cari)} hasil yang cocok.")

                data_tampil = []
                for i, r in enumerate(hasil_cari, 1):
                    kategori = kategori_by_index(records.index(r))
                    teks_bersih = re.sub(r"^\d+\.\s*", "", r)
                    bagian = teks_bersih.split("\t")
                    if len(bagian) >= 4:
                        nama_optk = bagian[0]
                        host = bagian[1]
                        media = bagian[2]
                        distribusi = bagian[3]
                    else:
                        nama_optk = bagian[0]
                        host = "-"
                        media = "-"
                        distribusi = "-"

                    data_tampil.append({
                        "No": i,
                        "Nama OPTK": nama_optk,
                        "Kategori": kategori,
                        "Host": host,
                        "Media Pembawa": media,
                        "Daerah Sebar": distribusi,
                        "Google": f"https://www.google.com/search?q={nama_optk.replace(' ', '+')}"
                    })

                df_tampil = pd.DataFrame(data_tampil)
                st.dataframe(df_tampil, use_container_width=True)

                # Tombol unduh CSV
                output3 = io.StringIO()
                writer3 = csv.DictWriter(output3, fieldnames=df_tampil.columns)
                writer3.writeheader()
                writer3.writerows(data_tampil)

                st.download_button(
                    label="💾 Download Hasil (CSV)",
                    data=output3.getvalue(),
                    file_name="hasil_cari_optk.csv",
                    mime="text/csv"
                )

            else:
                st.warning("❗ Tidak ditemukan hasil yang cocok berdasarkan nama OPTK.")
        else:
            st.warning("Masukkan minimal satu nama OPTK terlebih dahulu.")
