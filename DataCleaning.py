# Bibliotheken importieren
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno

# Zufallsseed setzen
np.random.seed(42)

# Datensatz einlesen
# df = pd.read_csv('ihr_datensatz.csv')
df = pd.read_csv('data/economy.csv')

# Dimensionen des Datensatzes
print(df.shape)

# Erste Zeilen anzeigen
print(df.head())

# Informationen zu Spalten und Datentypen
print(df.info())

# Fehlende Werte zählen
#df.isnull().sum()
df.isna().sum()

# Prozentsatz fehlender Werte berechnen
df.isna().mean()

round_data = []

for idx, row in df.iterrows():
    match_id = row['match_id']
    map_name = row['_map']
    team1_side = row['t1_start']
    team2_side = row['t2_start']
    
    for round_num in range(1, 31):
        winner_col = f'{round_num}_winner'
        team1_equip_col = f'{round_num}_t1'
        team2_equip_col = f'{round_num}_t2'
        
        if pd.notna(row[winner_col]):
            if round_num <= 15:
                current_team1_side = team1_side
                current_team2_side = team2_side
            else:
                current_team1_side = team2_side
                current_team2_side = team1_side
            
            t1_equip = int(row[team1_equip_col])
            t2_equip = int(row[team2_equip_col])
            equip_diff = t1_equip - t2_equip
            
            round_entry = {
                'match_id': int(match_id),
                'map': map_name,
                'round': int(round_num),
                'team1_equip': t1_equip,
                'team2_equip': t2_equip,
                'equipment_diff': equip_diff,
                'team1_side': current_team1_side,
                'team2_side': current_team2_side,
                'winner': int(row[winner_col])
            }
            
            round_data.append(round_entry)

df_rounds = pd.DataFrame(round_data)
df_rounds.to_csv("data/economy_rounds_cleaned.csv", index=False)

# Überprüfung: Sind alle fehlenden Werte behandelt?
df_rounds.isnull().sum()
df_rounds.isna().sum()

# Dimensionen prüfen
print(df_rounds.shape)

# Anzahl doppelter Zeilen
print(df_rounds.duplicated().sum())

# Duplikate entfernen
df_rounds = df_rounds.drop_duplicates()

# Neue Dimensionen prüfen
df_rounds.shape

# Datentypen überprüfen
df_rounds.dtypes

# Finale Übersicht
print("Finale Dimensionen:")
print(df_rounds.shape)

print("\nFehlende Werte:")
print(df_rounds.isnull().sum())

print("\nDatentypen:")
print(df_rounds.dtypes)

print("\nErste Zeilen des bereinigten Datensatzes:")
print(df_rounds.head())


df_rounds.to_csv('data/economy_rounds_cleaned.csv', index=False)

print("Bereinigter Datensatz wurde gespeichert!")
