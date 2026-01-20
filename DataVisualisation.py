# Bibliotheken importieren
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


# Bereinigten Datensatz einlesen
df = pd.read_csv('data/economy_rounds_cleaned.csv')

# Dimensionen
df.shape

# Erste Zeilen
df.head()

# Informationen zu Spalten
df.info()

# Statistische Übersicht
df.describe()

# Numerische Spalten identifizieren
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
print(f"Numerische Spalten: {list(numeric_cols)}")

# Visualisierung 1: [Welche Karten sind CT oder T-lastig?]

map_side_winrate = df[df['map'] != 'Default'].groupby(['map', 'team1_side'])['winner'].apply(lambda x: (x == 1).mean()).reset_index()

plt.figure(figsize=(12, 6))
sns.barplot(data=map_side_winrate, x='map', y='winner', hue='team1_side')
plt.title('Team1 Winrate pro Map und Side')
plt.xlabel('Map')
plt.ylabel('Winrate Team1')
plt.xticks(rotation=45)
plt.savefig('map_side_winrate.png', dpi=300, bbox_inches='tight')
plt.show()

# Visualisierung 2: [Wie stark beeinflusst Ökonomie den Runden-Ausgang?]

df['t1_win'] = (df['winner'] == 1).astype(int)
bins = [-5000, -2000, -1000, -500, 0, 500, 1000, 2000, 5000]
df['equip_bin'] = pd.cut(df['equipment_diff'], bins=bins)

bin_winrate = df.groupby('equip_bin', observed=False)['t1_win'].mean()

plt.figure(figsize=(12, 6))
bin_winrate.plot(kind='bar')
plt.title('Winrate von Team1 abhängig von Equipment Difference')
plt.xlabel('Equipment Diff Bins')
plt.ylabel('Winrate Team1')
plt.savefig('bin_winrate.png', dpi=300, bbox_inches='tight')
plt.show()

# Visualisierung 3: [Gibt es Match-Phasen, die "Seitenlastig" sind?]

round_winrate = df.groupby('round')['t1_win'].mean()

plt.figure(figsize=(12, 6))
round_winrate.plot()
plt.title('Team1 Winrate pro Runde')
plt.xlabel('Round')
plt.ylabel('Team1 Winrate')
plt.grid(True)
plt.savefig('round_winrate.png', dpi=300, bbox_inches='tight')
plt.show()

# Qualitätskontrolle: Überprüfen Sie Ihre Daten visuell

plt.figure(figsize=(10, 6))
sns.boxplot(data=df[['team1_equip', 'team2_equip']])
plt.title('Outlier-Check für Equipment')
plt.show()

print("Maps:", df['map'].unique())

print("Sides:", df['team1_side'].unique())

sns.countplot(data=df, x='winner')
plt.title('Gewinnerverteilung')
plt.show()
