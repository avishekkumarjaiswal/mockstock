import streamlit as st
import pandas as pd
import random
import os

# Set page config as the first Streamlit command
st.set_page_config(layout="wide")

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
    st.session_state.prediction = None  # Initialize prediction in session state
if 'players' not in st.session_state:
    st.session_state.players = {}  # Store player names and net worth
if 'show_success_message' not in st.session_state:
    st.session_state.show_success_message = False  # Flag to show success message

# Store passwords for each round in a dictionary
round_passwords = {
    1: "",  # Password for Round 1
    2: "password34",  # Password for Round 2
    3: "password56"   # Password for Round 3
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
        st.success(f"Successfully bought {shares} shares of {company}!")
        st.rerun()  # Force refresh to update the UI

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
        st.success(f"Successfully sold {shares} shares of {company}!")
        st.rerun()  # Force refresh to update the UI

# Function to get expert prediction
def get_expert_prediction(expert):
    if expert not in st.session_state.experts:
        return "Invalid expert selected."

    # Deduct the cost from the user's cash
    cost = st.session_state.experts[expert]["cost"]
    if st.session_state.cash < cost:
        return "Not enough cash to pay the expert!"

    st.session_state.cash -= cost  # Deduct the cost immediately

    # Generate a prediction based on the expert's accuracy
    accuracy = st.session_state.experts[expert]["accuracy"]
    if random.random() < accuracy:
        # Correct prediction
        prediction = f"{expert}'s prediction: The stock prices will rise in the next round!"
    else:
        # Incorrect prediction
        prediction = f"{expert}'s prediction: The stock prices will fall in the next round."

    return prediction

# Function to calculate net worth
def calculate_net_worth():
    current_prices = companies[f"Round {st.session_state.round}"]
    networth = st.session_state.cash
    for company, data in st.session_state.portfolio.items():
        current_price = current_prices.get(company, 0)  # Get current price or 0 if delisted
        networth += data['shares'] * current_price
    return networth

# Function to save leaderboard to CSV
def save_leaderboard():
    leaderboard_df = pd.DataFrame(list(st.session_state.players.items()), columns=["Player", "Net Worth (₹)"])
    leaderboard_df = leaderboard_df.sort_values(by="Net Worth (₹)", ascending=False)
    leaderboard_df.to_csv("leaderboard.csv", index=False)

# Function to load leaderboard from CSV
def load_leaderboard():
    if os.path.exists("leaderboard.csv"):
        try:
            leaderboard_df = pd.read_csv("leaderboard.csv")
            if not leaderboard_df.empty:  # Check if the file is not empty
                for _, row in leaderboard_df.iterrows():
                    st.session_state.players[row["Player"]] = row["Net Worth (₹)"]
        except pd.errors.EmptyDataError:
            st.warning("Leaderboard file is empty. Starting with a fresh leaderboard.")
    else:
        st.warning("Leaderboard file not found. Starting with a fresh leaderboard.")

# Load leaderboard data at the start
load_leaderboard()

# Streamlit app layout
st.title("F&IC LUCERIUM 2025")

# Player registration
if 'player_name' not in st.session_state:
    player_name = st.text_input("Enter your name to join the competition:")
    if st.button("Register"):
        if player_name:
            st.session_state.player_name = player_name
            st.session_state.players[player_name] = 0  # Initialize net worth to 0
            st.success(f"Welcome, {player_name}!")
            st.rerun()
else:
    st.sidebar.title("F&IC LUCERIUM 2025")
    st.sidebar.subheader(f"Cash in Hand (₹): {st.session_state.cash}")

    # Trade Shares section
    st.sidebar.subheader("Trade Shares")
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
    st.sidebar.subheader(f"Round {st.session_state.round} Password: `{round_passwords[st.session_state.round]}`")
    st.sidebar.subheader("Proceed to Next Round")
    password = st.sidebar.text_input("Enter Password to Proceed to Next Round", type="password")
    confirmation = st.sidebar.checkbox("I hereby confirm this.")

    # Submit Round button with confirmation check
    if st.sidebar.button("Submit Round"):
        if not confirmation:
            st.sidebar.error("Please confirm by checking the box above.")
        elif password == round_passwords[st.session_state.round]:  # Use the password from the dictionary
            if st.session_state.round < 3:
                # Update round and reset session state for the next round
                st.session_state.round += 1
                st.session_state.round_submitted = False
                st.session_state.prediction = None  # Clear prediction for the new round
                st.session_state.show_success_message = True  # Set flag to show success message

                # Force recalculation of portfolio data
                current_prices = companies[f"Round {st.session_state.round}"]
                for company, data in st.session_state.portfolio.items():
                    if data['shares'] > 0:
                        data['networth'] = data['shares'] * current_prices.get(company, 0)

                st.rerun()  # Force a rerun to update the UI instantly
            else:
                st.sidebar.error("All rounds completed!")
        else:
            st.sidebar.error("Incorrect password!")

    # Display success message after round submission
    if st.session_state.show_success_message:
        st.sidebar.success(f"Round {st.session_state.round - 1} submitted successfully! Now play the next round {st.session_state.round}.")
        st.session_state.show_success_message = False  # Reset the flag after displaying the message

    # Calculator in the sidebar
    st.sidebar.subheader("Calculator")
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
    st.sidebar.subheader("Get Expert Tips")
    expert_selected = st.sidebar.selectbox("Select an Expert", list(st.session_state.experts.keys()))
    expert_cost = st.session_state.experts[expert_selected]["cost"]
    st.sidebar.write(f"Cost: ₹{expert_cost}")

    # Button to get expert prediction
    if st.sidebar.button("Get Prediction"):
        prediction = get_expert_prediction(expert_selected)
        st.session_state.prediction = prediction  # Store prediction in session state
        st.rerun()  # Force a rerun to update the UI instantly

    # Display prediction if it exists
    if 'prediction' in st.session_state and st.session_state.prediction:
        st.sidebar.success(f"**Prediction:** {st.session_state.prediction}")  # Display prediction prominently
        st.sidebar.write(f"Remaining Cash: ₹{st.session_state.cash}")

    # Main content area
    st.header(f"Round {st.session_state.round}")

    # Display news articles for the current round
    st.subheader("News for This Round")
    for news in news_data[f"Round {st.session_state.round}"]:
        st.write(f"- {news}")

    # Create two columns for Current Stock Prices and Transaction Summary
    col1, col2 = st.columns(2)

    # Display company names and current prices in a table (left column)
    with col1:
        st.subheader("Current Stock Prices")
        current_prices_df = pd.DataFrame(list(current_prices.items()), columns=["Company", "Current Price (₹)"])
        st.table(current_prices_df)

    # Display Transaction Summary in a table (right column)
    with col2:
        st.subheader("Transaction Summary")
        current_round_transactions = [t for t in st.session_state.transactions if t['round'] == st.session_state.round]

        # Calculate total spent (only from buying shares)
        current_round_spent = sum(t['shares_bought'] * t['price'] for t in current_round_transactions)

        # Calculate total received (only from selling shares)
        current_round_received = sum(t['shares_sold'] * t['price'] for t in current_round_transactions)

        # Calculate net cash flow for the round
        net_cash_flow = current_round_received - current_round_spent

        # Create a DataFrame for the Transaction Summary
        transaction_summary_df = pd.DataFrame({
            "Metric": ["Total Amount Spent", "Total Amount Received", "Net Cash Flow"],
            "Amount (₹)": [current_round_spent, current_round_received, net_cash_flow]
        })
        st.table(transaction_summary_df)

    # Table for portfolio data (only display if there are transactions in the current round)
    st.subheader("Your Portfolio")
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
        st.write(f"**Total Portfolio Value (Networth): ₹{total_networth}**")
    else:
        st.write("No shares owned in the current round.")

    # Update player's net worth in the leaderboard
    st.session_state.players[st.session_state.player_name] = calculate_net_worth()

    # Display leaderboard
    st.subheader("Leaderboard")
    leaderboard_df = pd.DataFrame(list(st.session_state.players.items()), columns=["Player", "Net Worth (₹)"])
    leaderboard_df = leaderboard_df.sort_values(by="Net Worth (₹)", ascending=False)
    st.table(leaderboard_df)

    # Save leaderboard to CSV every second
    save_leaderboard()

    # Final winner announcement
    if st.session_state.round == 3 and password == round_passwords[st.session_state.round]:
        st.success("Competition completed! The winner is the one with the highest net worth.")
        save_leaderboard()  # Save leaderboard data to CSV
