import streamlit as st
import pandas as pd
import random
import os

# Set page config as the first Streamlit command
st.set_page_config(
    layout="wide",
    page_title="F&IC LUCERIUM 2025",
    page_icon="📈"
)

# Custom CSS for better design
st.markdown("""
    <style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none !important;}

    /* Custom styles for rumors submission */
    .rumor-form {
        background: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .rumor-form textarea {
        width: 100%;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    .rumor-form input {
        width: 100%;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    .rumor-form button {
        background: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
    }
    .rumor-form button:hover {
        background: #45a049;
    }

    /* Highlight current player in leaderboard */
    .leaderboard-table tr.highlight {
        background: #e3f2fd !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'cash' not in st.session_state:
    st.session_state.cash = 100000  # Starting cash in hand
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'round_submitted' not in st.session_state:
    st.session_state.round_submitted = False
if 'experts' not in st.session_state:
    st.session_state.experts = {
        "Expert 1": {"cost": 50000, "accuracy": 0.8},
        "Expert 2": {"cost": 30000, "accuracy": 0.49},
        "Expert 3": {"cost": 1000, "accuracy": 0.21}
    }
if 'prediction' not in st.session_state:
    st.session_state.prediction = None
if 'players' not in st.session_state:
    st.session_state.players = {}
if 'show_success_message' not in st.session_state:
    st.session_state.show_success_message = False
if 'rumors' not in st.session_state:
    st.session_state.rumors = []
if 'leaderboard_updated' not in st.session_state:
    st.session_state.leaderboard_updated = False

# Store passwords for each round in a dictionary
round_passwords = {
    1: "",
    2: "",
    3: ""
}

# Dummy data for companies and their prices for three rounds
companies = {
    'Round 1': {'Company A': 100, 'Company B': 150, 'Company C': 200},
    'Round 2': {'Company A': 110, 'Company B': 140, 'Company C': 210},
    'Round 3': {'Company A': 120, 'Company B': 130}  # Company C is delisted in Round 3
}

# Dummy news data for each round
news_data = {
    'Round 1': [
        "Company A announces record profits!",
        "Company B faces regulatory scrutiny.",
        "Company C launches a new product line."
    ],
    'Round 2': [
        "Company A's profits decline due to market conditions.",
        "Company B resolves regulatory issues and gains investor confidence.",
        "Company C's new product receives mixed reviews."
    ],
    'Round 3': [
        "Company A's stock surges after a major partnership.",
        "Company B's stock drops due to unexpected losses.",
        "Company C is delisted from the stock exchange."
    ]
}

# Function to load rumors from CSV
def load_rumors():
    if os.path.exists("rumors.csv"):
        try:
            rumors_df = pd.read_csv("rumors.csv")
            if not rumors_df.empty:
                # Return only the last 5 rumors and reverse the order (latest first)
                return rumors_df.to_dict('records')[-5:][::-1]
        except pd.errors.EmptyDataError:
            st.warning("Rumors file is empty.")
    return []

# Function to save rumors to CSV
def save_rumors(rumors):
    rumors_df = pd.DataFrame(rumors)
    rumors_df.to_csv("rumors.csv", index=False)

# Function to buy shares
def buy_shares(company, shares, current_price):
    total_cost = shares * current_price
    if total_cost > st.session_state.cash:
        st.error("Not enough cash to buy these shares!")
    else:
        if company not in st.session_state.portfolio:
            st.session_state.portfolio[company] = {'shares': 0, 'total_spent': 0, 'total_received': 0}
        st.session_state.portfolio[company]['shares'] += shares
        st.session_state.portfolio[company]['total_spent'] += total_cost
        st.session_state.cash -= total_cost
        st.session_state.transactions.append({
            'round': st.session_state.round,
            'company': company,
            'shares_bought': shares,
            'shares_sold': 0,
            'price': current_price
        })
        st.success(f"✅ Successfully bought {shares} shares of {company}!")
        st.rerun()

# Function to sell shares
def sell_shares(company, shares, current_price):
    if company not in st.session_state.portfolio or st.session_state.portfolio[company]['shares'] < shares:
        st.error("You don't own enough shares to sell!")
    else:
        total_received = shares * current_price
        st.session_state.portfolio[company]['shares'] -= shares
        st.session_state.portfolio[company]['total_received'] += total_received
        st.session_state.cash += total_received
        st.session_state.transactions.append({
            'round': st.session_state.round,
            'company': company,
            'shares_bought': 0,
            'shares_sold': shares,
            'price': current_price
        })
        st.success(f"✅ Successfully sold {shares} shares of {company}!")
        st.rerun()

# Function to get expert prediction
def get_expert_prediction(expert):
    if expert not in st.session_state.experts:
        return "Invalid expert selected."
    cost = st.session_state.experts[expert]["cost"]
    if st.session_state.cash < cost:
        return "Not enough cash to pay the expert!"
    st.session_state.cash -= cost
    accuracy = st.session_state.experts[expert]["accuracy"]
    if random.random() < accuracy:
        prediction = f"{expert}'s prediction: The stock prices will rise in the next round!"
    else:
        prediction = f"{expert}'s prediction: The stock prices will fall in the next round."
    return prediction

# Function to calculate net worth
def calculate_net_worth():
    current_prices = companies[f"Round {st.session_state.round}"]
    networth = st.session_state.cash
    for company, data in st.session_state.portfolio.items():
        current_price = current_prices.get(company, 0)
        networth += data['shares'] * current_price
    return networth

def save_leaderboard():
    # Unpack the dictionary to match the columns
    leaderboard_data = [
        [player, data["Net Worth (₹)"], data["Round"]]
        for player, data in st.session_state.players.items()
    ]
    leaderboard_df = pd.DataFrame(leaderboard_data, columns=["Player", "Net Worth (₹)", "Round"])
    leaderboard_df = leaderboard_df.sort_values(by="Net Worth (₹)", ascending=False)
    leaderboard_df.to_csv("leaderboard.csv", index=False)

# Function to load leaderboard from CSV
def load_leaderboard():
    if os.path.exists("leaderboard.csv"):
        try:
            leaderboard_df = pd.read_csv("leaderboard.csv")
            if not leaderboard_df.empty:
                for _, row in leaderboard_df.iterrows():
                    st.session_state.players[row["Player"]] = {
                        "Net Worth (₹)": row["Net Worth (₹)"],
                        "Round": row["Round"]
                    }
        except pd.errors.EmptyDataError:
            st.warning("Leaderboard file is empty. Starting with a fresh leaderboard.")
    else:
        st.warning("Leaderboard file not found. Starting with a fresh leaderboard.")

# Load leaderboard data at the start
load_leaderboard()

# Streamlit app layout
st.title("📈 F&IC LUCERIUM 2025")

# Player registration
if 'player_name' not in st.session_state:
    player_name = st.text_input("Enter your name to join the competition:")
    if st.button("Register"):
        if player_name:
            st.session_state.player_name = player_name
            st.session_state.players[player_name] = {"Net Worth (₹)": 0, "Round": 1}
            st.success(f"🎉 Welcome, {player_name}!")
            st.rerun()
else:
    # Display the player's name in the sidebar
    st.sidebar.write(f"👤 Hi, {st.session_state.player_name}!")
    
    st.sidebar.title("📊 F&IC LUCERIUM 2025")
    st.sidebar.subheader(f"💰 Cash in Hand (₹): {st.session_state.cash}")

    # Trade Shares section
    st.sidebar.subheader("💼 Trade Shares")
    current_prices = companies[f"Round {st.session_state.round}"]
    company_selected = st.sidebar.selectbox("Select Company", list(current_prices.keys()))
    shares = st.sidebar.number_input(f"Number of shares for {company_selected}", min_value=0, key=f"shares_{company_selected}")

    # Buy/Sell buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Buy"):
            buy_shares(company_selected, shares, current_prices[company_selected])
    with col2:
        if st.button("Sell"):
            sell_shares(company_selected, shares, current_prices[company_selected])

    # Proceed to Next Round section
    st.sidebar.subheader(f"🔑 Round {st.session_state.round} Password: `{round_passwords[st.session_state.round]}`")
    st.sidebar.subheader("⏭️ Proceed to Next Round")
    password = st.sidebar.text_input("Enter Password to Proceed to Next Round", type="password")
    confirmation = st.sidebar.checkbox("I hereby confirm this.")

    # Submit Round button with confirmation check
    if st.sidebar.button("Submit Round"):
        if not confirmation:
            st.sidebar.error("❌ Please confirm by checking the box above.")
        elif password == round_passwords[st.session_state.round]:
            if st.session_state.round < 3:
                st.session_state.round += 1
                st.session_state.round_submitted = False
                st.session_state.prediction = None
                st.session_state.show_success_message = True
                st.session_state.rumors = []
                st.session_state.players[st.session_state.player_name] = {
                    "Net Worth (₹)": calculate_net_worth(),
                    "Round": st.session_state.round
                }
                save_leaderboard()
                st.session_state.leaderboard_updated = True
                st.rerun()
            else:
                st.sidebar.error("🎉 All rounds completed!")
        else:
            st.sidebar.error("❌ Incorrect password!")

    # Display success message after round submission
    if st.session_state.show_success_message:
        st.sidebar.success(f"✅ Round {st.session_state.round - 1} submitted successfully! Now play the next round {st.session_state.round}.")
        st.session_state.show_success_message = False

    # Calculator in the sidebar
    st.sidebar.subheader("🧮 Calculator")
    calc_num1 = st.sidebar.number_input("Enter first number", key="calc_num1")
    calc_operation = st.sidebar.selectbox("Select operation", ["+", "-", "*", "/"], key="calc_operation")
    calc_num2 = st.sidebar.number_input("Enter second number", key="calc_num2")

    # Perform calculation
    if st.sidebar.button("Calculate"):
        if calc_operation == "+":
            result = calc_num1 + calc_num2
        elif calc_operation == "-":
            result = calc_num1 - calc_num2
        elif calc_operation == "*":
            result = calc_num1 * calc_num2
        elif calc_operation == "/":
            if calc_num2 != 0:
                result = calc_num1 / calc_num2
            else:
                result = "Error: Division by zero"
        else:
            result = "Invalid operation"
        st.sidebar.write(f"**Result:** {result}")

    # Expert Tips section
    st.sidebar.subheader("🔮 Get Expert Tips")
    expert_selected = st.sidebar.selectbox("Select an Expert", list(st.session_state.experts.keys()))
    expert_cost = st.session_state.experts[expert_selected]["cost"]
    st.sidebar.write(f"💸 Cost: ₹{expert_cost}")

    # Button to get expert prediction
    if st.sidebar.button("Get Prediction"):
        prediction = get_expert_prediction(expert_selected)
        st.session_state.prediction = prediction
        st.rerun()

    # Display prediction if it exists
    if 'prediction' in st.session_state and st.session_state.prediction:
        st.sidebar.success(f"**🔮 Prediction:** {st.session_state.prediction}")
        st.sidebar.write(f"💵 Remaining Cash: ₹{st.session_state.cash}")

    # Main content area
    st.header(f"📊 Round {st.session_state.round}")

    # Display news articles and rumors for the current round
    st.subheader("📰 News and Rumors for This Round")
    for news in news_data[f"Round {st.session_state.round}"]:
        st.write(f"- {news}")

    # Load and display rumors from CSV
    rumors = load_rumors()
    if rumors:
        st.write("**🗣️ Rumors:**")
        for rumor in rumors:
            st.write(f"- {rumor['source']}: {rumor['rumor']}")

    # Form to submit a rumor
    with st.form(key='rumor_form'):
        st.markdown("<div class='rumor-form'>", unsafe_allow_html=True)
        rumor_text = st.text_area("Submit a Rumor", placeholder="Enter your rumor here...", max_chars=200)
        rumor_source = st.text_input("Source (Optional, e.g., Anonymous)", placeholder="Anonymous")
        submit_rumor = st.form_submit_button("Submit Rumor")
        st.markdown("</div>", unsafe_allow_html=True)
        if submit_rumor and rumor_text:
            new_rumor = {"source": rumor_source if rumor_source else "Anonymous", "rumor": rumor_text}
            st.session_state.rumors.append(new_rumor)
            save_rumors(st.session_state.rumors)
            st.success("✅ Rumor submitted successfully!")
            st.rerun()

    # Create two columns for Current Stock Prices and Transaction Summary
    col1, col2 = st.columns(2)

    # Display company names and current prices in a table (left column)
    with col1:
        st.subheader("📈 Current Stock Prices")
        current_prices_df = pd.DataFrame(list(current_prices.items()), columns=["Company", "Current Price (₹)"])
        st.table(current_prices_df)

    # Display Transaction Summary in a table (right column)
    with col2:
        st.subheader("📝 Transaction Summary")
        current_round_transactions = [t for t in st.session_state.transactions if t['round'] == st.session_state.round]
        current_round_spent = sum(t['shares_bought'] * t['price'] for t in current_round_transactions)
        current_round_received = sum(t['shares_sold'] * t['price'] for t in current_round_transactions)
        net_cash_flow = current_round_received - current_round_spent
        transaction_summary_df = pd.DataFrame({
            "Metric": ["Total Amount Spent", "Total Amount Received", "Net Cash Flow"],
            "Amount (₹)": [current_round_spent, current_round_received, net_cash_flow]
        })
        st.table(transaction_summary_df)

    # Table for portfolio data (only display if there are transactions in the current round)
    st.subheader("💼 Your Portfolio")
    table_data = []
    total_spent = 0
    total_received = 0
    total_networth = 0

    # Only include companies with shares owned
    for company, data in st.session_state.portfolio.items():
        if data['shares'] > 0:  # Only include companies with shares owned
            current_price = current_prices.get(company, 0)  # Get current price or 0 if delisted
            networth = data['shares'] * current_price
            table_data.append([company, current_price, data['shares'], data['total_spent'], data['total_received'], networth])
            total_spent += data['total_spent']
            total_received += data['total_received']
            total_networth += networth

    # Display table only if there are transactions
    if table_data:
        df = pd.DataFrame(table_data, columns=["Company", "Current Price (₹)", "No. of shares", "Total amount spent", "Total amount received", "Networth"])
        st.table(df)
        st.write(f"**💰 Total Portfolio Value (Networth): ₹{total_networth}**")
    else:
        st.write("No shares owned in the current round.")

    # Display leaderboard with round progress
    st.subheader("🏆 Leaderboard")
    leaderboard_data = []
    for player, data in st.session_state.players.items():
        leaderboard_data.append([player, data["Net Worth (₹)"], data["Round"]])
    leaderboard_df = pd.DataFrame(leaderboard_data, columns=["Player", "Net Worth (₹)", "Round"])
    leaderboard_df = leaderboard_df.sort_values(by="Net Worth (₹)", ascending=False)

    # Highlight the current player's row
    def highlight_current_player(row):
        if row["Player"] == st.session_state.player_name:
            return ['background-color: #e3f2fd'] * len(row)
        else:
            return [''] * len(row)

    st.dataframe(leaderboard_df.style.apply(highlight_current_player, axis=1))

    # Final winner announcement
    if st.session_state.round == 3 and password == round_passwords[st.session_state.round]:
        st.success("🎉 Competition completed! The winner is the one with the highest net worth.")
        save_leaderboard()  # Save leaderboard data to CSV

# Help section in the sidebar
st.sidebar.subheader("❓ Help")
st.sidebar.write("""
- **Buy/Sell Shares**: Select a company and the number of shares to buy or sell.
- **Expert Tips**: Pay for expert predictions to guide your decisions.
- **Submit Round**: Enter the password to proceed to the next round.
- **Rumors**: Submit and view rumors to stay ahead of the competition.
""")

# Reset Game button (for admins)
if st.sidebar.button("🔄 Reset Game (Admin Only)"):
    st.session_state.clear()
    st.success("Game reset successfully! Refresh the page to start over.")
    st.rerun()
