import streamlit as st
import pandas as pd

st.set_page_config(page_title="📋 Pencarian OPTK & Target Sebar", layout="wide")

st.title("🪲 Sistem Pencarian & Analisis Target OPTK")

# === Tabs utama ===
tab1, tab2 = st.tabs(["🔍 Pencarian OPTK Berdasarkan Nama", "🎯 Analisis Target OPTK"])

# === Fungsi bantu kategori A1 dan A2 ===
def get_category(no, tipe):
    if tipe == "A1":
        if 2 <= no <= 237: return "Serangga"
        elif 239 <= no <= 262: return "Tungau"
        elif 264 <= no <= 278: return "Keong"
        elif 280 <= no <= 293: return "Siput"
        elif 295 <= no <= 360: return "Nematoda"
        elif 362 <= no <= 392: return "Gulma parasitik"
        elif 398 <= no <= 404: return "Gulma non parasitik"
        elif 406 <= no <= 538: return "Cendawan"
        elif 540 <= no <= 594: return "Bakteri"
        elif 596 <= no <= 610: return "Mollicute"
        elif 612 <= no <= 732: return "Virus"
        elif 733 <= no <= 739: return "Viroid"
    elif tipe == "A2":
        if 2 <= no <= 50: return "Serangga"
        elif 52 <= no <= 58: return "Tungau"
        elif 60 <= no <= 61: return "Keong"
        elif 63 <= no <= 72: return "Nematoda"
        elif 74 <= no <= 77: return "Gulma non parasitik"
        elif 79 <= no <= 108: return "Cendawan"
        elif 110 <= no <= 123: return "Bakteri"
        elif 125 <= no <= 136: return "Virus"
        elif no == 138: return "Viroid"
    return "-"

# === Simulasi DataFrame ===
data = {
    "No": [2, 3, 60, 65, 80, 125, 733],
    "Nama OPTK": ["Bactrocera dorsalis", "Bactrocera occipitalis", "Pomacea canaliculata",
                  "Meloidogyne incognita", "Fusarium oxysporum", "Banana bunchy top virus", "Coconut cadang-cadang viroid"],
    "Tipe": ["A1", "A1", "A1", "A1", "A1", "A1", "A1"],
    "Inang": ["Mangga", "Mangga", "Padi", "Tomat", "Pisang", "Pisang", "Kelapa"],
    "Daerah Sebar": ["Sumatera", "Jawa", "Sumatera", "Jawa", "Sulawesi", "Kalimantan", "Maluku"],
    "Media Pembawa": ["Buah", "Buah", "Air", "Tanah", "Batang", "Daun", "Batang"]
}
df = pd.DataFrame(data)
df["Kategori"] = df.apply(lambda x: get_category(x["No"], x["Tipe"]), axis=1)

# === TAB 1: Pencarian OPTK ===
with tab1:
    st.subheader("🔎 Pencarian Berdasarkan Nama OPTK")
    keyword = st.text_input("Masukkan nama OPTK (misal: *Bactrocera dorsalis*):")

    if keyword:
        results = df[df["Nama OPTK"].str.contains(keyword, case=False, na=False)]
        if not results.empty:
            grouped = results.groupby("Kategori")
            for kategori, group in grouped:
                st.markdown(f"### 🧩 {kategori}")
                st.dataframe(group[["Nama OPTK", "Inang", "Daerah Sebar", "Media Pembawa"]].drop_duplicates())
        else:
            st.warning("❌ Tidak ditemukan hasil yang cocok.")

# === TAB 2: Analisis Target OPTK ===
with tab2:
    st.subheader("🎯 Analisis Target OPTK Berdasarkan Sebaran")
    inang = st.text_input("Masukkan nama inang:")
    media = st.text_input("Masukkan media pembawa (opsional):")
    daerah_asal = st.text_input("Masukkan daerah sebar **asal**:")
    daerah_tujuan = st.text_input("Masukkan daerah sebar **tujuan**:")

    if st.button("Analisis Target"):
        if not inang or not daerah_asal or not daerah_tujuan:
            st.warning("⚠️ Harap isi *inang*, *daerah asal*, dan *daerah tujuan* minimal.")
        else:
            # Filter berdasarkan inang dan (opsional) media
            base_filter = df[df["Inang"].str.contains(inang, case=False, na=False)]
            if media:
                base_filter = base_filter[base_filter["Media Pembawa"].str.contains(media, case=False, na=False)]

            asal = base_filter[base_filter["Daerah Sebar"].str.contains(daerah_asal, case=False, na=False)]
            tujuan = base_filter[base_filter["Daerah Sebar"].str.contains(daerah_tujuan, case=False, na=False)]

            if asal.empty:
                st.info("ℹ️ Tidak ditemukan OPTK di daerah asal.")
            else:
                target_list = []
                for optk in asal["Nama OPTK"].unique():
                    if optk not in tujuan["Nama OPTK"].unique():
                        kategori = asal[asal["Nama OPTK"] == optk]["Kategori"].iloc[0]
                        target_list.append((optk, kategori))

                if target_list:
                    st.success("🎯 **Ada target OPTK:**")
                    for t in target_list:
                        st.markdown(f"- {t[0]} *(Kategori: {t[1]})*")
                else:
                    st.error("❌ Tidak ada target. Daerah tujuan sudah memiliki semua OPTK dari asal.")

            # Tampilkan hasil pengelompokan kategori
            grouped = base_filter.groupby("Kategori")
            st.markdown("---")
            st.markdown("### 📂 Pengelompokan OPTK Berdasarkan Kategori")
            for kategori, group in grouped:
                st.markdown(f"#### 🧩 {kategori}")
                st.dataframe(group[["Nama OPTK", "Inang", "Daerah Sebar", "Media Pembawa"]].drop_duplicates())
