import streamlit as st
import pandas as pd
import random

# Function to add randomness to projections and ownership
def add_randomness(value, randomness_factor=0.05):
    return value * (1 + random.uniform(-randomness_factor, randomness_factor))

# Function to generate lineups
def generate_lineups(df, max_player_exposure, total_lineups):
    player_usage = {player_id: 0 for player_id in df.index}
    generated_lineups = []

    for lineup_num in range(total_lineups):
        lineup = []
        
        # Sort players by a combination of projected points and randomness
        sorted_players = df.copy()
        sorted_players['randomized_proj_points'] = sorted_players['projected_fantasy_points'].apply(
            lambda x: add_randomness(x)
        )
        sorted_players['randomized_ownership'] = sorted_players['ownership'].apply(
            lambda x: add_randomness(x)
        )
        
        # Sort by randomized projections and ownership
        sorted_players = sorted_players.sort_values(by=['randomized_proj_points', 'randomized_ownership'], ascending=[False, True])
        
        # Iterate through positions to fill out a lineup
        for pos in ['QB', 'RB', 'WR', 'TE', 'D']:
            # Get available players for that position, respecting player exposure limits
            available_players = sorted_players[
                (sorted_players['position'] == pos) & 
                (player_usage[sorted_players.index] < max_player_exposure)
            ]
            
            # Select the top player for that position
            if not available_players.empty:
                selected_player = available_players.iloc[0]
                lineup.append(selected_player)
                player_usage[selected_player.name] += 1
        
        generated_lineups.append(lineup)
    return generated_lineups, player_usage

# Streamlit UI
st.title("NFL Lineup Generator")

# Input: Max player exposure and total lineups
max_player_exposure = st.sidebar.slider("Max Player Exposure", min_value=1, max_value=100, value=30)
total_lineups = st.sidebar.number_input("Total Lineups", min_value=1, max_value=150, value=70)

# Sample data - Replace this with your actual dataset
data = {
    'name': ['Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5'],
    'position': ['QB', 'RB', 'WR', 'TE', 'D'],
    'team': ['Team A', 'Team B', 'Team C', 'Team D', 'Team E'],
    'salary': [7000, 8000, 9000, 6000, 5000],
    'projected_fantasy_points': [20.0, 18.5, 19.0, 15.0, 8.0],
    'ownership': [10.0, 15.0, 12.0, 5.0, 2.0]
}

# Create a dataframe from the data
df = pd.DataFrame(data)

# Generate lineups based on input
if st.button("Generate Lineups"):
    lineups, player_usage = generate_lineups(df, max_player_exposure, total_lineups)
    
    # Display generated lineups
    st.write(f"Generated {len(lineups)} lineups:")
    for i, lineup in enumerate(lineups, 1):
        st.write(f"Lineup {i}:")
        st.table(pd.DataFrame(lineup))
    
    # Display player usage count
    player_usage_df = pd.DataFrame(list(player_usage.items()), columns=['Player', 'Usage Count'])
    st.write("Player Usage Count:")
    st.table(player_usage_df)
