import streamlit as st
from supabase import create_client, Client

# Połączenie
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    st.set_page_config(page_title="Zarządzanie Bazą", layout="wide")
    st.title("📦 System Magazynowy")

    t_dodaj, t_prody, t_katy = st.tabs(["➕ Dodaj", "📝 Edytuj Produkty", "🏷️ Kategorie"])

    # --- ZAKŁADKA: DODAWANIE ---
    with t_dodaj:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Nowa kategoria")
            with st.form("f_kat", clear_on_submit=True):
                n_k = st.text_input("Nazwa kategorii*")
                o_k = st.text_area("Opis")
                if st.form_submit_button("Zapisz"):
                    if n_k:
                        try:
                            supabase.table("kategorie").insert({"nazwa": n_k, "opis": o_k}).execute()
                            st.success("Dodano!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Błąd: {e}")
        with c2:
            st.subheader("Nowy produkt")
            kat_data = supabase.table("kategorie").select("id, nazwa").execute().data
            lista_kat = {k['nazwa']: k['id'] for k in kat_data}
            with st.form("f_prod", clear_on_submit=True):
                n_p = st.text_input("Nazwa produktu*")
                l_p = st.number_input("Ilość", min_value=0, step=1)
                c_p = st.number_input("Cena", min_value=0.0)
                k_p = st.selectbox("Kategoria", options=list(lista_kat.keys()))
                if st.form_submit_button("Zapisz"):
                    if n_p:
                        try:
                            supabase.table("produkty").insert({
                                "nazwa": n_p, "liczba": l_p, "cena": c_p, "kategoria_id": lista_kat[k_p]
                            }).execute()
                            st.success("Dodano produkt!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Błąd: {e}")

    # --- ZAKŁADKA: EDYCJA I USUWANIE PRODUKTÓW ---
    with t_prody:
        st.subheader("Lista produktów")
        prody = supabase.table("produkty").select("*").execute().data
        if prody:
            for p in prody:
                with st.expander(f"📦 {p['nazwa']} (ID: {p['id']})"):
                    col_a, col_b, col_c = st.columns(3)
                    e_nazwa = col_a.text_input("Nazwa", value=p['nazwa'], key=f"en_{p['id']}")
                    e_liczba = col_b.number_input("Ilość", value=int(p['liczba']), key=f"el_{p['id']}")
                    e_cena = col_c.number_input("Cena", value=float(p['cena']), key=f"ec_{p['id']}")
                    
                    btn_upd, btn_del = st.columns(2)
                    if btn_upd.button("Zapisz zmiany", key=f"bu_{p['id']}", use_container_width=True):
                        supabase.table("produkty").update({
                            "nazwa": e_nazwa, "liczba": e_liczba, "cena": e_cena
                        }).eq("id", p['id']).execute()
                        st.success("Zaktualizowano!")
                        st.rerun()
                    
                    if btn_del.button("Usuń produkt", key=f"bd_{p['id']}", use_container_width=True, type="primary"):
                        supabase.table("produkty").delete().eq("id", p['id']).execute()
                        st.rerun()
        else:
            st.info("Baza produktów jest pusta.")

    # --- ZAKŁADKA: KATEGORIE ---
    with t_katy:
        st.subheader("Zarządzanie kategoriami")
        kat_list = supabase.table("kategorie").select("*").execute().data
        for k in kat_list:
            col_k1, col_k2 = st.columns([4, 1])
            col_k1.write(f"🏷️ **{k['nazwa']}** — {k['opis']}")
            if col_k2.button("Usuń", key=f"dk_{k['id']}", use_container_width=True):
                try:
                    supabase.table("kategorie").delete().eq("id", k['id']).execute()
                    st.rerun()
                except:
                    st.error("Nie można usunąć – kategoria zawiera produkty!")

if __name__ == "__main__":
    main()
