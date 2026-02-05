import streamlit as st
from supabase import create_client
import os

# ================== SUPABASE ==================
SUPABASE_URL = "PUT_SUPABASE_URL_HERE"
SUPABASE_KEY = "PUT_SUPABASE_ANON_KEY_HERE"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="TALENT HOUSE",
    page_icon="🔥",
    layout="centered"
)

# ================== UI STYLE ==================
st.markdown("""
<style>
body { background-color:#0a041a; color:white; }
.stButton button {
    background:#a855f7;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ================== SESSION ==================
if "user" not in st.session_state:
    st.session_state.user = None

# ================== AUTH ==================
def login():
    st.title("TALENT HOUSE 🔥")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if res.user:
            user = supabase.table("users").select("*").eq("id", res.user.id).execute()
            st.session_state.user = user.data[0]
            st.rerun()

def signup():
    st.title("Create Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    username = st.text_input("Username")
    role = st.selectbox("Role", ["scout", "skiller"])

    if st.button("Sign Up"):
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        tokens = 30 if role == "skiller" else 0

        supabase.table("users").insert({
            "id": res.user.id,
            "username": username,
            "role": role,
            "tokens": tokens
        }).execute()

        st.success("Account Created 🔥")

# ================== SCOUT ==================
def scout_dashboard():
    st.header("Scout Dashboard 🎯")

    category = st.selectbox("Filter Category", ["All", "Music", "Writing", "Art", "General"])

    query = supabase.table("posts").select("*").order("total_rating", desc=True)
    posts = query.execute().data

    for post in posts:
        if category != "All" and post["category"] != category:
            continue

        st.subheader(post["category"])
        st.write(post["content"])
        st.write(f"⭐ Rating: {post['total_rating']}")

        rate = st.slider("Rate", 1, 10, key=post["id"])
        if st.button("Submit Rating", key=f"r{post['id']}"):
            supabase.table("ratings").insert({
                "scout_id": st.session_state.user["id"],
                "post_id": post["id"],
                "value": rate
            }).execute()

            new_rating = (post["total_rating"] + rate) / 2
            supabase.table("posts").update({
                "total_rating": new_rating
            }).eq("id", post["id"]).execute()

            st.success("Rated 🔥")
            st.rerun()

# ================== SKILLER ==================
def skiller_dashboard():
    st.header("Skiller Dashboard 🌟")
    st.write(f"Tokens: {st.session_state.user['tokens']}")

    category = st.selectbox("Category", ["Music", "Writing", "Art", "General"])
    content = st.text_area("Show your talent")

    if st.button("Post"):
        supabase.table("posts").insert({
            "skiller_id": st.session_state.user["id"],
            "category": category,
            "content": content,
            "developer_rating": 5,
            "total_rating": 5
        }).execute()
        st.success("Posted 🔥")
        st.rerun()

# ================== ADMIN ==================
def admin_dashboard():
    st.header("Admin Panel 👑")

    users = supabase.table("users").select("*").execute().data
    for u in users:
        col1, col2 = st.columns(2)
        col1.write(f"{u['username']} ({u['role']})")
        if col2.button("Toggle Active", key=u["id"]):
            supabase.table("users").update({
                "active": not u["active"]
            }).eq("id", u["id"]).execute()
            st.rerun()

# ================== MAIN ==================
if st.session_state.user is None:
    page = st.radio("Choose", ["Login", "Sign Up"])
    if page == "Login":
        login()
    else:
        signup()
else:
    role = st.session_state.user["role"]
    if role == "scout":
        scout_dashboard()
    elif role == "skiller":
        skiller_dashboard()
    else:
        admin_dashboard()

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()
