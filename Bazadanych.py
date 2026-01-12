import streamlit as st
from supabase import create_client, Client

# Połączenie z Supabase (dane z Streamlit Secrets)
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

def main():
    st.set_page_config(page_title="Magazyn", layout="wide")
    st.title("📦 System Zarządzania")

    tab_dodaj, tab_produkty, tab_kategorie = st.tabs([
        "➕ Dodaj Nowe", "📑 Lista Produktów", "🏷️ Kategorie"
    ])

    # --- TAB: DODAWANIE ---
    with tab_dodaj:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Nowa Kategoria")
            with st.form("form_kat", clear_on_submit=True):
                n_kat = st.text_input("Nazwa*")
                o_kat = st.text_area("Opis")
                if st.form_submit_button("Zapisz kategorię"):
                    if n_kat:
                        supabase.table("kategorie").insert({"nazwa": n_kat, "opis": o_kat}).execute()
                        st.success("Dodano!")
                        st.rerun()

        with col2:
            st.subheader("Nowy Produkt")
            kats = supabase.table("kategorie").select("id, nazwa").execute().data
            opcje_kat = {k['nazwa']: k['id'] for k in kats}
            
            with st.form("form_prod", clear_on_submit=True):
                n_prod = st.text_input("Nazwa produktu*")
                l_prod = st.number_input("Liczba", min_value=0)
                c_prod = st.number_input("Cena", min_value=0.0)
                sel_kat = st.selectbox("Kategoria", options=list(opcje_kat.keys()))
                
                if st.form_submit_button("Zapisz produkt"):
                    if n_prod:
                        supabase.table("produkty").insert({
                            "nazwa": n_prod, "liczba": l_prod, 
                            "cena": c_prod, "kategoria_id": opcje_kat[sel_kat]
                        }).execute()
                        st.success("Dodano!")
                        st.rerun()

    # --- TAB: LISTA I EDYCJA PRODUKTÓW ---
    with tab_produkty:
        st.subheader("Zarządzaj Produktami")
        produkty = supabase.table("produkty").select("*").execute().data
        
        if produkty:
            # Nagłówki "tabeli"
            h1, h2, h3, h4, h5 = st.columns([3, 1, 1, 1, 1])
            h1.write("**Nazwa**")
            h2.write("**Ilość**")
            h3.write("**Cena**")
            h4.write("**Akcja**")
            h5.write("**Usuń**")
            st.divider()

            for p in produkty:
                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
                    
                    # Pola do edycji
                    nowa_nazwa = c1.text_input("n", value=p['nazwa'], key=f"n_{p['id']}", label_visibility="collapsed")
                    nowa_ilosc = c2.number_input("i", value=int(p['liczba']), key=f"i_{p['id']}", label_visibility="collapsed")
                    nowa_cena = c3.number_input("c", value=float(p['cena']), key=f"c_{p['id']}", label_visibility="collapsed")
                    
                    # Przycisk Aktualizacji
                    if c4.button("Zapisz", key=f"upd_{p['id']}", use_container_width=True):
                        supabase.table("produkty").update({
                            "nazwa": nowa_nazwa,
                            "liczba": nowa_ilosc,
                            "cena": nowa_cena
                        }).eq("id", p['id']).execute()
                        st.toast(f"Zaktualizowano: {nowa_nazwa}")
                        st.rerun()

                    # Przycisk Usuwania
                    if c5.button("🗑️", key=f"del_{p['id']}", use_container_width=True):
                        supabase.table("produkty").delete().eq("id", p['id']).execute()
                        st.rerun()
        else:
            st.info("Brak produktów w bazie.")

    # --- TAB: KATEGORIE ---
    with tab_kategorie:
        st.subheader("Lista Kategorii")
        kategorie = supabase.table("kategorie").select("*").execute().data
        
        for k in kategorie:
            col_txt, col_btn = st.columns([5, 1])
            col_txt.write(f"🏷️ **{k['nazwa']}** — {k['opis']}")
            if col_btn.button("Usuń", key=f"dk_{k['id']}", use_container_width=True):
                try:
                    supabase.table("kategorie").delete().eq("id", k['id']).execute()
                    st.rerun()
                except:
                    st.error("Nie można usunąć! Kategoria jest przypisana do produktów.")

if __name__ == "__main__":
    main()
