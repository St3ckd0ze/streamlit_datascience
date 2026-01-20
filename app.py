import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# Seite konfigurieren
st.set_page_config(page_title='CS:GO Economy Analysis')

@st.cache_data
def load_data():
    # Daten laden
    file_path = 'data/economy_rounds_cleaned.csv'
    df = pd.read_csv(file_path)
    
    # Berechnen ob Team 1 gewonnen hat
    df['team1_win'] = (df['winner'] == 1).astype(int)
    
    # Geld-Differenz in Gruppen einteilen
    bins = [-np.inf, -20000, -10000, -5000, -2000, 0, 2000, 5000, 10000, 20000, np.inf]
    labels = ['< -20k', '-20k bis -10k', '-10k bis -5k', '-5k bis -2k', '-2k bis 0', '0 bis 2k', '2k bis 5k', '5k bis 10k', '10k bis 20k', '> 20k']
    df['diff_bin'] = pd.cut(df['equipment_diff'], bins=bins, labels=labels)
    
    return df

def main():
    # Titel
    st.title('CS:GO Analytics')
    st.write('Interaktive Datenanalyse der Spielrunden')
    
    # Daten laden
    df = load_data()

    # Sidebar für die Filter-Einstellungen
    st.sidebar.header('Filter')
    
    # Eine Map auswählen
    all_maps = sorted(df['map'].unique())
    selected_map = st.sidebar.selectbox(
        'Map wählen:',
        options=['Alle Maps'] + all_maps
    )
    
    # Auswahl Team-Seite
    selected_side = st.sidebar.radio(
        'Team-Seite (Team 1):',
        ['Alle', 'Terrorist', 'Counter-Terrorist']
    )
    
    # Auswahl Geld-Bereiche
    st.sidebar.write('Geld-Vorteil Bereiche:')
    all_bins = df['diff_bin'].cat.categories.tolist()
    
    # Spalten für "an/aus" Buttons
    col_a, col_b = st.sidebar.columns(2)
    if col_a.button('Alle an'):
        for b in all_bins:
            st.session_state[f'bin_{b}'] = True
    if col_b.button('Alle aus'):
        for b in all_bins:
            st.session_state[f'bin_{b}'] = False

    selected_bins = []
    for bin_label in all_bins:
        # Checkbox mit Session State verknüpfen
        key = f'bin_{bin_label}'
        if key not in st.session_state:
            st.session_state[key] = True
            
        if st.sidebar.checkbox(bin_label, key=key):
            selected_bins.append(bin_label)
    
    # Sichern der Auswahl
    if not selected_bins:
        st.warning('Bitte wähle mindestens einen Bereich aus!')
        return

    # Nach Map filtern
    if selected_map == 'Alle Maps':
        filtered_df = df
    else:
        filtered_df = df[df['map'] == selected_map]
    
    # Nach Team-Seite filtern
    if selected_side != 'Alle':
        # Mapping von den Anzeigenamen auf die Datenwerte 't' und 'ct'
        side_mapping = {'Terrorist': 't', 'Counter-Terrorist': 'ct'}
        filtered_df = filtered_df[filtered_df['team1_side'] == side_mapping[selected_side]]
        
    # Nach ausgewählten Geld-Bereichen filtern
    filtered_df = filtered_df[filtered_df['diff_bin'].isin(selected_bins)]

    # Wichtige Kennzahlen
    st.subheader('Wichtige Statistiken')
    col1, col2, col3 = st.columns(3)
    
    total_rounds = len(filtered_df)
    win_rate = filtered_df['team1_win'].mean() * 100 if total_rounds > 0 else 0
    avg_diff = filtered_df['equipment_diff'].mean()
    
    col1.metric('Gespielte Runden', f"{total_rounds:,}")
    col2.metric('Gewinnrate', f"{win_rate:.1f}%")
    col3.metric('Ø Geld-Differenz', f"${avg_diff:,.0f}")

    # Visualisierungen in Tabs
    tab1, tab2, tab3 = st.tabs(["Gewinnrate Analyse", "Map Vergleich", "Rohdaten"])

    with tab1:
        st.subheader('Siegchance nach Geld-Vorteil')
        
        # Gewinnrate pro Gruppe
        bin_analysis = filtered_df.groupby('diff_bin', observed=True)['team1_win'].agg(['mean', 'count']).reset_index()
        bin_analysis = bin_analysis[bin_analysis['count'] > 10]
        
        # Balkendiagramm
        fig_winrate = px.bar(
            bin_analysis, 
            x='diff_bin', 
            y='mean',
            title='Gewinnwahrscheinlichkeit je nach Ausrüstungswert',
            labels={'mean': 'Gewinnrate (%)', 'diff_bin': 'Geld-Differenz (Team 1 vs Team 2)'},
            color='mean',
            color_continuous_scale='RdYlGn',
            template='plotly_dark',
            range_y=[0, 1.01] # Etwas höherer Wert, damit Linie sichtbar ist
        )
        # Säulen anpassen (Breite)
        fig_winrate.update_traces(width=0.4)
        
        # Y-Achse als Prozent
        fig_winrate.update_yaxes(tickformat=".0%", dtick=0.1)
        
        # 50% Linie
        fig_winrate.add_hline(y=0.5, line_dash="dash", line_color="white")
        st.plotly_chart(fig_winrate, use_container_width=True)

    with tab2:
        st.subheader('Vergleich der Karten')
        
        # Gewinnrate pro Map
        map_winrate = filtered_df.groupby('map')['team1_win'].mean().sort_values(ascending=False).reset_index()
        
        fig_map = px.bar(
            map_winrate,
            x='map',
            y='team1_win',
            title='Gewinnrate pro Karte',
            labels={'team1_win': 'Gewinnrate (%)', 'map': 'Karte'},
            color='team1_win',
            template='plotly_dark',
            range_y=[0, 1.01]
        )
        # Säulen anpassen (Breite)
        fig_map.update_traces(width=0.4)
        
        # Prozent-Formatierung und Gitterlinien
        fig_map.update_yaxes(tickformat=".0%", dtick=0.1)
        
        st.plotly_chart(fig_map, use_container_width=True)

    with tab3:
        # Rohdaten
        if st.checkbox('Zeige die ersten 100 Zeilen der Daten'):
            st.dataframe(filtered_df.head(100), use_container_width=True)

    # Fußzeile
    st.markdown('---')
    st.write('Datenquelle: [Kaggle CS:GO Dataset](https://www.kaggle.com/datasets/mateusdmachado/csgo-professional-matches)')

if __name__ == '__main__':
    main()