import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io

from database import init_db, SessionLocal, Expense, Portfolio
from auth import authenticate_user, create_user

# --- PAGE SETUP ---
st.set_page_config(page_title="Finance Tracker", page_icon="💸", layout="wide")

# --- CUSTOM CSS FOR BEAUTIFUL UI ---
st.markdown("""
<style>
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-title {
        font-size: 1.1rem;
        color: #FAFAFA;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .metric-value-negative {
        font-size: 2rem;
        font-weight: bold;
        color: #FF5252;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database tables
init_db()

# --- UTILS ---
def get_db():
    return SessionLocal()

def export_to_excel(df, filename):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

# --- AUTHENTICATION UI ---
def login_ui():
    st.title("💸 Personal Finance Tracker")
    st.markdown("### Please login or create an account to continue")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                user = authenticate_user(username, password)
                if user:
                    st.session_state['user_id'] = user.id
                    st.session_state['username'] = user.username
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    
    with tab2:
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            submitted = st.form_submit_button("Sign Up")
            
            if submitted:
                if len(new_username) < 3 or len(new_password) < 5:
                    st.error("Username must be at least 3 characters and password 5 characters.")
                else:
                    success = create_user(new_username, new_password)
                    if success:
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username already exists!")

def logout_ui():
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Logged in as: {st.session_state['username']}**")
    if st.sidebar.button("Logout"):
        st.session_state['user_id'] = None
        st.session_state['username'] = None
        st.rerun()

# --- APP SECTIONS ---

def show_dashboard(db):
    st.title("📊 Dashboard")
    user_id = st.session_state['user_id']
    
    # Fetch Data
    expenses_db = db.query(Expense).filter(Expense.user_id == user_id).all()
    portfolio_db = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    
    # Process Expenses
    df_exp = pd.DataFrame([{
        "amount": e.amount,
        "type": e.type,
        "date": e.date,
        "category": e.category
    } for e in expenses_db])
    
    # Key Metrics
    total_income = df_exp[df_exp['type'] == 'Income']['amount'].sum() if not df_exp.empty else 0
    total_expense = df_exp[df_exp['type'] == 'Expense']['amount'].sum() if not df_exp.empty else 0
    balance = total_income - total_expense
    
    # Process Portfolio
    df_port = pd.DataFrame([{
        "invested": p.invested_amount,
        "current": p.current_value
    } for p in portfolio_db])
    
    total_invested = df_port['invested'].sum() if not df_port.empty else 0
    total_current = df_port['current'].sum() if not df_port.empty else 0
    portfolio_growth = total_current - total_invested
    
    # Display Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        color = "metric-value" if balance >= 0 else "metric-value-negative"
        st.markdown(f'<div class="metric-card"><div class="metric-title">Balance</div><div class="{color}">₹{balance:,.2f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Income</div><div class="metric-value">₹{total_income:,.2f}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Expenses</div><div class="metric-value-negative">₹{total_expense:,.2f}</div></div>', unsafe_allow_html=True)
    with col4:
        # Portfolio value
        color = "metric-value" if portfolio_growth >= 0 else "metric-value-negative"
        st.markdown(f'<div class="metric-card"><div class="metric-title">Portfolio Value</div><div class="{color}">₹{total_current:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Expenses by Category")
        if not df_exp.empty and len(df_exp[df_exp['type'] == 'Expense']) > 0:
            exp_only = df_exp[df_exp['type'] == 'Expense']
            fig1 = px.pie(exp_only, values='amount', names='category', hole=0.4, 
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No expense data available to show chart.")
            
    with col_chart2:
        st.subheader("Income vs Expense Trend")
        if not df_exp.empty:
            df_exp['date'] = pd.to_datetime(df_exp['date'])
            trend_df = df_exp.groupby(['date', 'type'])['amount'].sum().reset_index()
            fig2 = px.bar(trend_df, x='date', y='amount', color='type', barmode='group',
                          color_discrete_map={'Income': '#4CAF50', 'Expense': '#FF5252'})
            fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No transaction data available.")

def show_expenses(db):
    st.title("💸 Expenses & Income")
    user_id = st.session_state['user_id']
    
    # Define categories
    expense_categories = ["Housing", "Food", "Transportation", "Utilities", "Insurance", "Healthcare", "Entertainment", "Personal", "Debt", "Other"]
    income_categories = ["Salary", "Business", "Freelance", "Investments", "Gifts", "Other"]
    
    with st.expander("➕ Add New Transaction", expanded=False):
        with st.form("add_transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                t_type = st.selectbox("Type", ["Expense", "Income"])
                amount = st.number_input("Amount", min_value=0.01, format="%.2f")
                t_date = st.date_input("Date", date.today())
            with col2:
                category = st.selectbox("Category", expense_categories + income_categories)
                notes = st.text_input("Notes")
            
            submitted = st.form_submit_button("Save Transaction")
            if submitted:
                new_exp = Expense(
                    user_id=user_id,
                    amount=amount,
                    category=category,
                    date=t_date,
                    notes=notes,
                    type=t_type
                )
                db.add(new_exp)
                db.commit()
                st.success("Transaction added successfully!")
                st.rerun()

    # Filters
    st.markdown("### Search & Filter")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    # Query Data
    query = db.query(Expense).filter(Expense.user_id == user_id)
    
    all_records = query.order_by(Expense.date.desc()).all()
    if not all_records:
        st.info("No transactions found.")
        return

    df = pd.DataFrame([{
        "ID": e.id,
        "Date": e.date,
        "Type": e.type,
        "Category": e.category,
        "Amount": e.amount,
        "Notes": e.notes
    } for e in all_records])
    
    with f_col1:
        q_type = st.multiselect("Filter Type", ["Expense", "Income"])
    with f_col2:
        all_cats = sorted(df['Category'].unique().tolist())
        q_cat = st.multiselect("Filter Category", all_cats)
    with f_col3:
        unique_months = sorted(list(set(df['Date'].apply(lambda x: x.strftime('%Y-%m')))), reverse=True)
        q_month = st.selectbox("Filter Month", ["All"] + unique_months)

    if q_type:
        df = df[df['Type'].isin(q_type)]
    if q_cat:
        df = df[df['Category'].isin(q_cat)]
    if q_month != "All":
        df = df[df['Date'].apply(lambda x: x.strftime('%Y-%m')) == q_month]

    st.dataframe(df.drop(columns=['ID']), use_container_width=True, hide_index=True)
    
    excel_data = export_to_excel(df.drop(columns=['ID']), "transactions.xlsx")
    st.download_button(
        label="📄 Export to Excel",
        data=excel_data,
        file_name="transactions.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Deletion
    st.markdown("#### Manage Transactions")
    del_col1, del_col2, _ = st.columns([2, 2, 4])
    with del_col1:
        del_id = st.selectbox("Select Transaction ID to Delete", df['ID'].tolist()) if not df.empty else None
    with del_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Delete Selected Transaction") and del_id:
            db.query(Expense).filter(Expense.id == del_id).delete()
            db.commit()
            st.success("Deleted!")
            st.rerun()

def show_portfolio(db):
    st.title("📈 Portfolio Manager")
    user_id = st.session_state['user_id']
    
    with st.expander("➕ Add Investment", expanded=False):
        with st.form("add_portfolio_form"):
            col1, col2 = st.columns(2)
            with col1:
                asset_type = st.selectbox("Asset Type", ["Mutual Fund", "Stock", "Crypto", "Fixed Deposit", "Other"])
                category = st.selectbox("Category / Market Cap", ["Large Cap", "Mid Cap", "Small Cap", "Flexi Cap", "Bluechip", "Altcoin", "N/A"])
                name = st.text_input("Asset Name (e.g., HDFC Midcap, BTC, AAPL)")
            with col2:
                invested_amount = st.number_input("Total Invested Amount", min_value=0.0)
                current_value = st.number_input("Current Value", min_value=0.0)
            
            submitted = st.form_submit_button("Add Investment")
            if submitted and name:
                new_port = Portfolio(
                    user_id=user_id,
                    asset_type=asset_type,
                    category=category,
                    name=name,
                    invested_amount=invested_amount,
                    current_value=current_value
                )
                db.add(new_port)
                db.commit()
                st.success("Investment added successfully!")
                st.rerun()
                
    st.markdown("### Current Portfolio")
    
    query = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    df = pd.DataFrame([{
        "ID": p.id,
        "Asset Type": p.asset_type,
        "Category": p.category,
        "Name": p.name,
        "Invested": p.invested_amount,
        "Current Value": p.current_value,
        "Growth (Abs)": p.current_value - p.invested_amount,
        "Growth (%)": ((p.current_value - p.invested_amount) / p.invested_amount * 100) if p.invested_amount > 0 else 0
    } for p in query])
    
    if not df.empty:
        display_df = df.copy()
        display_df['Invested'] = display_df['Invested'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Current Value'] = display_df['Current Value'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Growth (Abs)'] = display_df['Growth (Abs)'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Growth (%)'] = display_df['Growth (%)'].apply(lambda x: f"{x:,.2f}%")
        
        st.dataframe(display_df.drop(columns=['ID']), use_container_width=True, hide_index=True)
        
        # Totals
        tot_invested = df['Invested'].sum()
        tot_current = df['Current Value'].sum()
        net_growth = tot_current - tot_invested
        net_growth_pct = (net_growth / tot_invested * 100) if tot_invested > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Invested", f"₹{tot_invested:,.2f}")
        c2.metric("Total Current Value", f"₹{tot_current:,.2f}")
        c3.metric("Overall Growth", f"₹{net_growth:,.2f}", f"{net_growth_pct:,.2f}%")
        
        # Charts
        st.markdown("---")
        ch1, ch2 = st.columns(2)
        with ch1:
            st.subheader("Asset Allocation")
            fig1 = px.pie(df, values='Current Value', names='Asset Type', hole=0.3)
            st.plotly_chart(fig1, use_container_width=True)
        with ch2:
            st.subheader("Category Allocation")
            fig2 = px.pie(df, values='Current Value', names='Category', hole=0.3)
            st.plotly_chart(fig2, use_container_width=True)
            
        excel_data = export_to_excel(df.drop(columns=['ID']), "portfolio.xlsx")
        st.download_button(
            label="📄 Export Portfolio to Excel",
            data=excel_data,
            file_name="portfolio.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Deletion
        st.markdown("#### Manage Asset")
        del_col1, del_col2, _ = st.columns([2, 2, 4])
        with del_col1:
            del_id = st.selectbox("Select Asset ID to Delete", df['ID'].tolist())
        with del_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Delete Asset"):
                db.query(Portfolio).filter(Portfolio.id == del_id).delete()
                db.commit()
                st.success("Deleted!")
                st.rerun()
    else:
        st.info("No portfolio added yet.")

# --- MAIN APP LOGIC ---
def main():
    if 'user_id' not in st.session_state or st.session_state['user_id'] is None:
        login_ui()
    else:
        # User is logged in
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Dashboard", "Expenses", "Portfolio"])
        
        logout_ui()
        
        db = get_db()
        try:
            if page == "Dashboard":
                show_dashboard(db)
            elif page == "Expenses":
                show_expenses(db)
            elif page == "Portfolio":
                show_portfolio(db)
        finally:
            db.close()

if __name__ == "__main__":
    main()
