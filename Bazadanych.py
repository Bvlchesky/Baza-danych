import streamlit as st
from supabase import create_client, Client

# Połączenie (wymaga st.secrets["SUPABASE_URL"] i st.secrets["SUPABASE_KEY"])
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def main():
    st.set_page_config(page_title="Magazyn Pro", layout="wide")
    st.title("📦 Panel Zarządzania Magazynem")

    t_list, t_add, t_cat = st.tabs(["📑 Lista i Edycja", "➕ Dodaj Nowy", "🏷️ Kategorie"])

    # --- TAB: LISTA I EDYCJA ---
    with t_list:
        st.subheader("Aktualny stan magazynowy")
        try:
            prods = supabase.table("produkty").select("*").order("id").execute().data
            if prods:
                for p in prods:
                    with st.expander(f"Produkt: {p['nazwa']} (ID: {p['id']})"):
                        col1, col2, col3 = st.columns(3)
                        new_n = col1.text_input("Nazwa", value=p['nazwa'], key=f"n_{p['id']}")
                        new_l = col2.number_input("Ilość", value=int(p['liczba']), key=f"l_{p['id']}")
                        new_c = col3.number_input("Cena", value=float(p['cena']), key=f"c_{p['id']}")
                        
                        b_up, b_del = st.columns(2)
                        if b_up.button("Zapisz zmiany", key=f"u_{p['id']}", use_container_width=True):
                            supabase.table("produkty").update({
                                "nazwa": new_n, "liczba": new_l, "cena": new_c
                            }).eq("id", p['id']).execute()
                            st.success("Zapisano!")
                            st.rerun()
                        
                        if b_del.button("Usuń całkowicie", key=f"d_{p['id']}", use_container_width=True, type="primary"):
                            supabase.table("produkty").delete().eq("id", p['id']).execute()
                            st.rerun()
            else:
                st.info("Brak produktów.")
        except Exception as e:
            st.error(f"Błąd pobierania: {e}")

    # --- TAB: DODAWANIE ---
    with t_add:
        st.subheader("Dodaj nowy produkt")
        try:
            kats = supabase.table("kategorie").select("id, nazwa").execute().data
            lista_kategorii = {k['nazwa']: k['id'] for k in kats}
            
            with st.form("add_form", clear_on_submit=True):
                name = st.text_input("Nazwa produktu*")
                qty = st.number_input("Ilość", min_value=0, step=1)
                price = st.number_input("Cena", min_value=0.0)
                cat_name = st.selectbox("Wybierz kategorię", options=list(lista_kategorii.keys()))
                
                if st.form_submit_button("Dodaj do bazy"):
                    if name:
                        # WAŻNE: Nie wysyłamy 'id' - baza sama go nada
                        nowy_produkt = {
                            "nazwa": name,
                            "liczba": qty,
                            "cena": price,
                            "kategoria_id": lista_kategorii[cat_name]
                        }
                        supabase.table("produkty").insert(nowy_produkt).execute()
                        st.success(f"Dodano: {name}")
                        st.rerun()
                    else:
                        st.warning("Podaj nazwę produktu!")
        except Exception as e:
            st.error(f"Najpierw dodaj kategorie! Błąd: {e}")

    # --- TAB: KATEGORIE ---
    with t_cat:
        st.subheader("Zarządzanie kategoriami")
        with st.form("kat_form", clear_on_submit=True):
            kn = st.text_input("Nowa kategoria")
            ko = st.text_area("Opis kategorii")
            if st.form_submit_button("Dodaj kategorię"):
                if kn:
                    supabase.table("kategorie").insert({"nazwa": kn, "opis": ko}).execute()
                    st.rerun()

        st.divider()
        all_kats = supabase.table("kategorie").select("*").execute().data
        for k in all_kats:
            ck1, ck2 = st.columns([4, 1])
            ck1.write(f"📁 **{k['nazwa']}** (ID: {k['id']})")
            if ck2.button("Usuń", key=f"dk_{k['id']}"):
                try:
                    supabase.table("kategorie").delete().eq("id", k['id']).execute()
                    st.rerun()
                except:
                    st.error("Nie można usunąć kategorii, która ma przypisane produkty!")

if __name__ == "__main__":
    main()
