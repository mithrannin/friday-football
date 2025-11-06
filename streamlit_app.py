import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from itertools import combinations

# def load_data(data):
#     return pd.read_csv(data)

# df = load_data("data/ff25test.csv")


url = "https://docs.google.com/spreadsheets/d/1Qk1A-UVgPKnoGDnP4ZNtri0ucLn-cf2hmiIv41LdLPE/edit?usp=sharing"

conn = st.connection("gsheets", type = GSheetsConnection)
df = conn.read(spreadsheet = url, worksheet = "1405471253")
df.index += 1
df.index.name = "Rank"

dfLeaderboard = df.copy()
dfLeaderboard['Change'] = dfLeaderboard['Change'].fillna(0)
dfLeaderboard.drop(dfLeaderboard.tail(1).index,inplace=True)
dfLeaderboard = dfLeaderboard.astype({'Change' : 'int', 'Games' : 'int', 'Wins' : 'int', 'Losses' : 'int'})

dfPlayers = df[['Player','Rating']].copy()

dfMatches = conn.read(spreadsheet = url, worksheet = "1358750119")
dfMatches = dfMatches.astype(str)

dfMatch1 = dfMatches.head(2)
dfMatch2 = dfMatches.iloc[2:4]
dfMatch3 = dfMatches.iloc[4:6]

## 

def make_teams(activePlayers):
    players = activePlayers
    
    closest_difference = None
    second_best = None
    all_players_set = set(players.keys())
    team_size = int(len(players)/2)
    
    for team_a in combinations(players.keys(), team_size):
        team_a_set = set(team_a)
        team_b_set = all_players_set - team_a_set
    
        team_a_total = sum([players[x] for x in team_a_set])
        team_b_total = sum([players[x] for x in team_b_set])
    
        score_difference = abs(team_a_total - team_b_total)
    
        if not closest_difference or score_difference < closest_difference:
            closest_difference = score_difference
            best_team_a = team_a_set     
            best_team_b = team_b_set
            
    for team_a in combinations(players.keys(), team_size):
        team_a_set = set(team_a)
        team_b_set = all_players_set - team_a_set
        
        team_a_total = sum([players[x] for x in team_a_set])
        team_b_total = sum([players[x] for x in team_b_set])
    
        score_difference = abs(team_a_total - team_b_total)
        
        if (not second_best or score_difference < second_best) and len(team_a_set.difference(best_team_a)) >= int(len(players)/4) and len(team_a_set.difference(best_team_b)) >= int(len(players)/4):
            second_best = score_difference
            second_team_a = team_a_set
            second_team_b = team_b_set
        
    
    team1 = pd.DataFrame(list(best_team_a))
    team1.columns = ["Player"]
    team2 = pd.DataFrame(list(best_team_b))
    team2.columns = ["Player"]
    
    score1 = sum(players[x] for x in best_team_a)
    score2 = sum(players[x] for x in best_team_b)
    
    team1b = pd.DataFrame(list(second_team_a))
    team1b.columns = ["Player"]
    team2b = pd.DataFrame(list(second_team_b))
    team2b.columns = ["Player"]
    
    score1b = sum(players[x] for x in second_team_a)
    score2b = sum(players[x] for x in second_team_b)
    
    return team1, team2, score1, score2, team1b, team2b, score1b, score2b
    
def display_teams(team1, team2, score1, score2, team1b, team2b, score1b, score2b):
    st.header("Suggested teams")
    st.subheader("Best variant")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Team 1")
        st.caption(f"Total rating: {score1:.2f}")
        st.dataframe(team1, hide_index=True)
    with col2:
        st.subheader("Team 2")
        st.caption(f"Total rating: {score2:.2f}")
        st.dataframe(team2, hide_index=True)
    st.divider()
    st.subheader("Runner up variant")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Team 1")
        st.caption(f"Total rating: {score1b:.2f}")
        st.dataframe(team1b, hide_index=True)
    with col2:
        st.subheader("Team 2")
        st.caption(f"Total rating: {score2b:.2f}")
        st.dataframe(team2b, hide_index=True)
    st.divider()


def color_format(value):
    if value < 0:
        color = 'red' 
    elif value > 0:
        color = 'green'
    elif value == 0:
        color = 'black'
    return 'color: %s' % color

    
##

def home_page():
    st.title("Leaderboard")
    st.subheader("Matches played: 3")
    
    # st.dataframe(df)
    
    st.dataframe(dfLeaderboard.style.applymap(color_format, subset = ['Change']), height = 35 * len(dfLeaderboard) + 38)
    
def match_page():
    st.title("Match History")
    st.subheader("Matches played: 3")
    
    st.dataframe(dfMatch1.style.highlight_max(subset = ['Score'], color = 'palegreen'), hide_index=True)
    st.dataframe(dfMatch2.style.highlight_max(subset = ['Score'], color = 'palegreen'), hide_index=True)
    st.dataframe(dfMatch3.style.highlight_max(subset = ['Score'], color = 'palegreen'), hide_index=True)
    
def matchmaking():
    st.title("Matchmaking tool")
    
    st.subheader("Players coming on Friday")
    
    allPlayerList = dfPlayers['Player'].tolist()
    
    activePlayers = st.multiselect(
        "Players coming",
        allPlayerList,
        [],
        )
    
    st.divider()
    
    st.write("We have " + str(len(activePlayers)) + " players coming:")
    st.session_state['activePlayers'] = activePlayers
    
    dfActive = dfPlayers[dfPlayers['Player'].isin(activePlayers)]
    playersToMatch = dict(zip(dfActive['Player'],dfActive['Rating']))
    
    st.dataframe(dfActive)
    
    st.divider()
    
    # team_size_label = "Players per team"
    # team_size = st.number_input(
    #     label = team_size_label,
    #     value = 5,
    #     min_value = 3,
    #     max_value = 6,
    #     step = 1,
    #     format = "%i",
    #     disabled=False,
    #     label_visibility = "visible")
    
    matchmaking_label = "Create teams"
    if st.button(
            label = matchmaking_label,
            type = "primary",
            use_container_width=False):
       team1, team2, score1, score2, team1b, team2b, score1b, score2b = make_teams(playersToMatch)
       display_teams(team1, team2, score1, score2, team1b, team2b, score1b, score2b) 
        
        
        
    
    
leaderboard = st.Page(home_page, title = "Leaderboard", icon = "🏆")
matchHistory = st.Page(match_page, title = "Match History", icon = "📆")
matchmaker = st.Page(matchmaking, title = "Matchmaking tool", icon = "🔥")


# Navbar
pg = st.navigation({"Stats": [leaderboard, matchHistory],
                    "Tools": [matchmaker]})

pg.run()

st.sidebar.markdown("# Games played: 2")
st.sidebar.markdown("# Next game: April 18th")