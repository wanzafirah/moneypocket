"""Pocket Money Tracker — a pastel, student-friendly Streamlit app.

Run locally:      streamlit run app.py
Deploy:           push this folder to GitHub, then deploy app.py on share.streamlit.io
"""

import calendar
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------- config
st.set_page_config(page_title="Pocket Money Tracker", page_icon="🎀", layout="wide")

DATA_FILE = Path(__file__).parent / "transactions.csv"
COLUMNS = ["date", "type", "category", "amount", "note"]

EXPENSE_CATS = [
    "🧋 Drinks",
    "🍜 Food",
    "🚌 Transport",
    "📚 Printing & Books",
    "🎮 Fun",
    "👕 Shopping",
    "📱 Top-up",
    "🎁 Other",
]

# One-tap buttons for things students actually buy.
QUICK_ADD = {
    "🧋 Bubble tea": ("🧋 Drinks", 6.50),
    "🍜 Canteen food": ("🍜 Food", 8.00),
    "🚌 Bus / LRT": ("🚌 Transport", 2.50),
    "🖨️ Print notes": ("📚 Printing & Books", 5.00),
    "🎬 Movie night": ("🎮 Fun", 15.00),
}

CAT_COLORS = {
    "🧋 Drinks": "#FFB7C5",
    "🍜 Food": "#FFDAC1",
    "🚌 Transport": "#A8D8EA",
    "📚 Printing & Books": "#C7CEEA",
    "🎮 Fun": "#F8C8DC",
    "👕 Shopping": "#D8C4F0",
    "📱 Top-up": "#B5EAD7",
    "🎁 Other": "#E2F0CB",
    "💵 Allowance": "#9FE2BF",
}

# ----------------------------------------------------------------- cute CSS
st.markdown(
    """
    <style>
      .stApp {
        background: linear-gradient(135deg, #FFF5F8 0%, #F1F7FF 50%, #F4FFF8 100%);
      }
      h1, h2, h3 { color: #000000; }
      .hero {
        background: linear-gradient(120deg, #FFD1DC 0%, #C7CEEA 50%, #B5EAD7 100%);
        padding: 22px 26px; border-radius: 22px; margin-bottom: 18px;
        box-shadow: 0 6px 18px rgba(180, 160, 200, 0.25);
      }
      .hero h1 { margin: 0; font-size: 2rem; color: #000000; }
      .hero p  { margin: 6px 0 0; color: #000000; font-size: 1rem; }
      div[data-testid="stMetric"] {
        background: #FFFFFFCC; border: 2px solid #FFE3EE;
        border-radius: 18px; padding: 12px 16px;
        box-shadow: 0 4px 14px rgba(190, 175, 210, 0.18);
      }
      div[data-testid="stMetricLabel"] { color: #000000; }
      .stButton > button {
        border-radius: 999px; border: 2px solid #FFC9DD;
        background: #FFF0F5; color: #000000; font-weight: 600;
        padding: 0.35rem 1rem; transition: all .15s ease;
      }
      .stButton > button:hover { background: #FFE0EC; border-color: #FF9EB5; }
      .stTabs [data-baseweb="tab-list"] { gap: 8px; }
      .stTabs [data-baseweb="tab"] {
        background: #FFFFFFAA; border-radius: 999px; padding: 6px 18px;
        border: 2px solid #EDE4FF;
      }
      .stTabs [aria-selected="true"] { background: #FFD1DC !important; border-color: #FF9EB5 !important; }
      .tip {
        background: #FFFDF3; border: 2px dashed #FFE0A3; border-radius: 16px;
        padding: 12px 16px; color: #000000;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------- data layer
def load_data() -> pd.DataFrame:
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df
    return pd.DataFrame(columns=COLUMNS)


def save_data(df: pd.DataFrame) -> None:
    df.to_csv(DATA_FILE, index=False)


def add_entry(txn_date, kind: str, category: str, amount: float, note: str) -> None:
    df = load_data()
    new_row = pd.DataFrame(
        [[txn_date, kind, category, round(float(amount), 2), note]], columns=COLUMNS
    )
    save_data(pd.concat([df, new_row], ignore_index=True))
    st.session_state.pop("df_cache", None)


if "amount" not in st.session_state:
    st.session_state.amount = 0.0
if "cat_choice" not in st.session_state:
    st.session_state.cat_choice = EXPENSE_CATS[0]
if "note" not in st.session_state:
    st.session_state.note = ""

# Widgets can only be reset *before* they are drawn, so we do it here.
if st.session_state.pop("reset_form", False):
    st.session_state.amount = 0.0
    st.session_state.note = ""

df = load_data()
expenses = df[df["type"] == "Expense"] if not df.empty else df
income = df[df["type"] == "Income"] if not df.empty else df
today = date.today()

spent_month = float(
    expenses.loc[expenses["date"] >= today.replace(day=1), "amount"].sum()
)
spent_today = float(expenses.loc[expenses["date"] == today, "amount"].sum())

# ----------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### 🎀 Your pocket settings")
    budget = st.number_input(
        "Monthly pocket money (RM)", min_value=0.0, value=300.0, step=10.0
    )
    savings_goal = st.number_input(
        "Savings goal this month (RM)", min_value=0.0, value=50.0, step=10.0
    )
    st.divider()
    st.download_button(
        "⬇️ Download my records",
        data=df.to_csv(index=False).encode("utf-8") if not df.empty else b"date,type,category,amount,note\n",
        file_name="pocket_money.csv",
        mime="text/csv",
    )
    if not df.empty and st.button("🧹 Clear everything"):
        save_data(pd.DataFrame(columns=COLUMNS))
        st.rerun()

# ----------------------------------------------------------------- hero
st.markdown(
    f"""
    <div class="hero">
      <h1>Hi friend, it's {today.strftime('%A, %d %b')} 🌷</h1>
      <p>Small steps every day. You've spent <b>RM {spent_today:,.2f}</b> today — let's keep it mindful!</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_add, tab_stats, tab_goal = st.tabs(["➕ Add money move", "📊 Where it went", "🎯 Saving jar"])

# ----------------------------------------------------------------- tab 1
with tab_add:
    st.subheader("⚡ Tap once for the usual suspects")
    cols = st.columns(len(QUICK_ADD))
    for col, (label, (cat, price)) in zip(cols, QUICK_ADD.items()):
        if col.button(label, width="stretch"):
            st.session_state.cat_choice = cat
            st.session_state.amount = price

    st.subheader("✍️ Or write it yourself")
    with st.form("add_form", clear_on_submit=False):
        left, right = st.columns([1, 1])
        with left:
            txn_date = st.date_input("When was it?", value=today)
            kind = st.radio("Type", ["Expense", "Income"], horizontal=True)
        with right:
            cat = st.selectbox("Category", EXPENSE_CATS, key="cat_choice")
            amount = st.number_input("How much? (RM)", min_value=0.0, step=0.50, key="amount")

        note = st.text_input("Fun note (optional)", placeholder="bubble tea with Mei 🌸", key="note")
        submitted = st.form_submit_button("💖 Save it", width="stretch")

    if submitted:
        if amount <= 0:
            st.warning("Pop in an amount bigger than RM 0 first 🌱")
        elif kind == "Expense":
            add_entry(txn_date, kind, cat, amount, note)
            st.session_state.reset_form = True
            st.success(f"Saved! RM {amount:,.2f} on {cat}. Nice tracking 💗")
            st.rerun()
        else:
            add_entry(txn_date, kind, "💵 Allowance", amount, note or "Pocket money in")
            st.session_state.reset_form = True
            st.success(f"Yay, RM {amount:,.2f} added to your pocket 🎉")
            st.rerun()

    if not df.empty:
        st.divider()
        st.caption("Latest moves")
        recent = df.sort_values("date", ascending=False).tail(5)[
            ["date", "type", "category", "amount", "note"]
        ]
        st.dataframe(recent, width="stretch", hide_index=True)

# ----------------------------------------------------------------- tab 2
with tab_stats:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💸 Spent today", f"RM {spent_today:,.2f}")
    c2.metric("📅 Spent this month", f"RM {spent_month:,.2f}")
    left_to_spend = max(budget - spent_month, 0.0)
    c3.metric("👜 Left in pocket", f"RM {left_to_spend:,.2f}")
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    days_left = max((last_day - today).days + 1, 1)
    c4.metric("☕ Safe to spend / day", f"RM {left_to_spend / days_left:,.2f}")

    st.progress(
        min(spent_month / budget, 1.0) if budget > 0 else 0.0,
        text=f"Monthly budget used: RM {spent_month:,.2f} / RM {budget:,.2f}",
    )

    if expenses.empty:
        st.info("No expenses yet — add one and your charts will bloom here 🌼")
    else:
        left, right = st.columns([1, 1])
        with left:
            by_cat = expenses.groupby("category", as_index=False)["amount"].sum()
            fig = px.pie(
                by_cat,
                names="category",
                values="amount",
                hole=0.55,
                title="What my money became 🍩",
                color="category",
                color_discrete_map=CAT_COLORS,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#000000",
                legend_title_text="",
            )
            st.plotly_chart(fig, width="stretch")

        with right:
            last14 = pd.date_range(today - timedelta(days=13), today)
            daily = (
                expenses.groupby("date")["amount"].sum().reindex(last14, fill_value=0)
            )
            fig2 = px.bar(
                x=[d.strftime("%d %b") for d in daily.index],
                y=daily.values,
                title="My last 14 days 🌈",
                color_discrete_sequence=["#FFB7C5"],
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#000000",
                xaxis_title="",
                yaxis_title="RM",
            )
            st.plotly_chart(fig2, width="stretch")

        no_spend_days = int(
            sum(
                1
                for d in pd.date_range(today - timedelta(days=6), today)
                if d not in set(expenses["date"])
            )
        )
        st.markdown(
            f"""<div class="tip">🧘 <b>No-spend days this week:</b> {no_spend_days} / 7 —
            {['keep going, you got this!', 'nice rhythm!', 'wow, wallet champion!'][min(no_spend_days // 3, 2)]}</div>""",
            unsafe_allow_html=True,
        )

        st.divider()
        if st.button("↩️ Undo my last entry"):
            keep = df.drop(df.index[-1])
            save_data(keep)
            st.rerun()

# ----------------------------------------------------------------- tab 3
with tab_goal:
    st.subheader("🎯 My saving jar")
    saved = max(budget - spent_month, 0.0)
    ratio = min(saved / savings_goal, 1.0) if savings_goal > 0 else 0.0

    jar = int(ratio * 10)
    st.markdown(f"## {'🫙' + '🪙' * jar + '·' * (10 - jar)}")
    st.progress(ratio, text=f"RM {saved:,.2f} kept out of RM {savings_goal:,.2f} goal")

    if ratio >= 1:
        st.balloons()
        st.success("Goal smashed! Treat yourself a little — you earned it 🎉")
    elif ratio >= 0.5:
        st.info("Halfway there! A few more mindful days and the jar is full 💪")
    else:
        st.info("Every ringgit counts. Try one no-bubble-tea day this week? 🧋➡️🚫")

    st.markdown(
        '<div class="tip">💡 <b>Student trick:</b> move RM 2 into savings every time you '
        "skip a snack you didn't really want. It adds up faster than you think!</div>",
        unsafe_allow_html=True,
    )

st.caption("Made with 💗 — your records are saved in transactions.csv next to this app.")
