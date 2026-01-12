import streamlit as st
from supabase import create_client, Client

# Konfiguracja połączenia z Supabase
# Najbezpieczniej trzymać te dane w Streamlit Secrets (na GitHubie nie podajemy ich wprost!)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    st.set_page_config(page_title="Zarządzanie Kategoriami", page_icon="📦")
    
    st.title("➕ Dodaj nową kategorię")
    st.write("Użyj poniższego formularza, aby dodać wpis do tabeli `kategorie`.")

    # Formularz dodawania kategorii
    with st.form("category_form", clear_on_submit=True):
        # Zgodnie ze schematem: nazwa (text), opis (text)
        # Pole 'id' jest zazwyczaj generowane automatycznie (int8)
        nazwa = st.text_input("Nazwa kategorii*", placeholder="np. Elektronika")
        opis = st.text_area("Opis kategorii", placeholder="Krótki opis grupy produktów...")

        submit_button = st.form_submit_button("Zapisz w bazie")

    if submit_button:
        if not nazwa:
            st.error("Pole 'Nazwa' jest wymagane!")
        else:
            try:
                # Przygotowanie danych do wysłania
                data = {
                    "nazwa": nazwa,
                    "opis": opis
                }
                
                # Wykonanie zapytania INSERT do Supabase
                response = supabase.table("kategorie").insert(data).execute()
                
                st.success(f"Pomyślnie dodano kategorię: **{nazwa}**")
                st.balloons()
                
            except Exception as e:
                st.error(f"Wystąpił błąd podczas zapisywania: {e}")

    # Sekcja podglądu aktualnych kategorii
    st.divider()
    st.subheader("📋 Aktualne kategorie w bazie")
    
    try:
        res = supabase.table("kategorie").select("*").execute()
        if res.data:
            st.table(res.data)
        else:
            st.info("Baza kategorii jest pusta.")
    except Exception as e:
        st.error("Nie udało się pobrać listy kategorii.")

if __name__ == "__main__":
    main()
