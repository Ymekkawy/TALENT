import streamlit as st
from datetime import datetime
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------- CONFIG ----------------
st.set_page_config(page_title="TALENT HOUSE", layout="wide")
st.title("TALENT HOUSE")

# ---------------- MODERN NEON BACKGROUND ----------------
st.markdown(
    """
    <style>
    /* Background gradient neon purple + black */
    .stApp {
        background: linear-gradient(135deg, #1f005c, #4b0082);
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    /* Buttons */
    div.stButton > button {
        background-color: #8a2be2;
        color: white;
        border-radius: 12px;
        height: 3em;
        width: 12em;
        font-weight: bold;
        font-size: 16px;
        border: 2px solid #d8b6ff;
    }
    div.stButton > button:hover {
        background-color: #d8b6ff;
        color: #4b0082;
        border: 2px solid #8a2be2;
    }
    /* Inputs */
    input, textarea, select {
        background-color: #2a1a4d;
        color: white;
        border: 2px solid #8a2be2;
        border-radius: 8px;
        padding: 5px;
    }
    /* Sidebar */
    .css-1d391kg {
        background-color: #1a0b3d;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- ADMIN LOGIN INFO ----------------
ADMIN_USERNAME = "dev"
ADMIN_PASSWORD = "152007poco"

# ---------------- PAYMENT & TOKENS ----------------
PAYMENT_NUMBER = "01000004397"
TOKEN_PACKAGES = {
    "30 Tokens": (100, 30),
    "60 Tokens": (90, 60),
    "600 Tokens": (1500, 600)
}

# ---------------- FIREBASE ----------------
if not firebase_admin._apps:
    cred_dict = {
        "type": "service_account",
        "project_id": "talent-199e5",
        "private_key_id": "f687fdbe55873a2b8a665edc40408a21e9e288ea",
        "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDUbIiOm6fruwt4
XowfBM0u/Il6FJiUyBCLdSXqcYXOVlA6/Gwd/5OxAIEo/Tp0rX1xyH3OZv5Njuiu
wwZt7PTyeBVbhCYsoIwWVGthneynbV2DIiWobQrsGcFp8vaxGOp0jrS+KkauTWpY
q2QAKlg4VEHQvwttclcTVsatnSsOLtvtA8NUm7AT1SN8sMK14qFquKLfCkaKskBC
/6z0AqhcF3oBr8kANKxKBWssV9oDQ28J+2Lcq7Q9zLxjNGOJ7weeI4e0HVJAIl0f
0b+OjLfL/0XxtFABQlUgl4d68BvYbVi8nuNQHInhXZ5DmUD5w8IkLyjsV73ZB8CR
UBlzjpFPAgMBAAECggEAAYW+As7XYlqgVFGewN6PCk4RpCs/a4DCXmWA18Nn7JjB
kXKoSbZaHIbyGTubYb7k98RMMCCcpCyo7g7qxGEe4X/+OZfJK3SCth3bxfYH5Kx/
FfoDYBSL/MsAdl4Hg5eeOPPVR5Ztx3Q5lcuz3azWatNVXdKIsyICWsEHKOZhkR2K
50xU5jHlmDSatxj47G9K9Z4HGng3IpzM8c9LDyPSU3/h8mYfAknwe0qEgsjnh94o
4QYHnuCLKX9OsQBiCCtjI6CbqKJFmGkRqcLN4smnrEj2HdnYl0XfDbwQR9BLt8wm
JCizze5IOACGZeDwN5q6fcH3J2AWa5aAuOolvPzhGQKBgQD/bat0eImNNVN40xQQ
V/BAg/ELjtEfle5KMt450b2Z+buCXPHVv1X+y8Mgmm3RS4BltOxuA5alLe7pRcMP
3rxYdjQqRc+Fc29I+HZ19TrHbYIFHLjjIdzlJu1t/0kUmI8nvVzTDuqXhttHDYFm
cUq6Q+xqSL1Xq1HfN2NWDTaAtwKBgQDU5jorXSLD7IOsBiosuNlBgJf/sBVlSs5X
EpANk7Njc6HCn08kPv2K3gVbIzXkwtTHZJZDVA9sdSZD4GnXe41RWTwA6qmtCLoD
109FdgjRR9oSHcOJee63NRAs2Aw5EZzuLBcUpr3GKQ0a3+eDCF26KZc3xtgLVevH
LizwWG+sKQKBgHSntrVz04ZtQ1kcNb6dGvmsCKt5p2Kgi/rRLpMDim9HEe8g2cYA
I5tBnjVGsj7zF4nbzlsUQnnf94wMM2ENHcHdAkgIKBXPuZR+/UM0I4svJUGGc54w
Of1iAO/Ktqq0XjUNE9bEqjlX+s+BiIar2TAmk1ObMvZWJQcn+bM0R58TAoGBALOn
X7jODBM211nnjdlVVwfeQuWhqjxipsJ1SJgcZklq/zqjgn48pWl0tyJUERtsiW+E
4wQHwEguh07J5abPfM4Dtg2z9+CrN4UcQKmF1CT+M/gLo8Cz4ww4u+CLo6zYvwuA
qy1jE0tPwt5FyTAadDUu+Ys4wYC3TZIz1fovNnUZAoGBAM+uer4di9d+qe8N+Sxc
nl3jEIvgFlLHIGm6DWvaQ/IrBJLQ39vN/qm+SRXnwbEYHSE1NHJK8lFdEvte4167
s2AgahPiZjG4PLCc6aSdOWyienl8dlUc80G/BUrDCyWiyEG9cX4nPYx5qrPof4qZ
c/TblbNRQugIConFluGP1O/d
-----END PRIVATE KEY-----""",
        "client_email": "firebase-adminsdk-fbsvc@talent-199e5.iam.gserviceaccount.com",
        "client_id": "112925563666280259221",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc@talent-199e5.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------- UTILITY FUNCTIONS ----------------
def get_user(username):
    user_ref = db.collection("users").document(username).get()
    if user_ref.exists:
        return user_ref.to_dict()
    return None

def create_user(username, password, role):
    if get_user(username):
        return False
    db.collection("users").document(username).set({
        "password": password,
        "role": role,
        "tokens": 30 if role=="skiller" else 0,
        "profile_pic": None,
        "banned": False
    })
    return True

def ban_user(username):
    db.collection("users").document(username).update({"banned": True})

# ---------------- LOGIN / SIGNUP ----------------
st.sidebar.title("Login / SignUp")
choice = st.sidebar.selectbox("Action", ["Login","SignUp"])

if choice=="SignUp":
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    role = st.sidebar.selectbox("Role", ["skiller","scout"])
    if st.sidebar.button("Sign Up"):
        if create_user(username, password, role):
            st.success("Account created! You can login now.")
        else:
            st.error("Username already exists.")

elif choice=="Login":
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username==ADMIN_USERNAME and password==ADMIN_PASSWORD:
            st.session_state['role'] = 'admin'
            st.session_state['username'] = ADMIN_USERNAME
        else:
            user = get_user(username)
            if user and user["password"]==password:
                if user.get("banned"):
                    st.error("This account is banned.")
                else:
                    st.session_state['role'] = user["role"]
                    st.session_state['username'] = username
            else:
                st.error("Invalid login")

# ---------------- AFTER LOGIN ----------------
if 'role' in st.session_state:
    role = st.session_state['role']
    username = st.session_state['username']

    if role=="skiller":
        st.header(f"Welcome Skiller: {username}")

        # Profile picture
        profile_pic_file = st.file_uploader("Upload profile picture", type=['png','jpg','jpeg'])
        if profile_pic_file:
            db.collection("users").document(username).update({"profile_pic": profile_pic_file.getvalue()})
            image = Image.open(profile_pic_file)
            st.image(image, caption="Profile picture")
            if st.button("Delete profile picture"):
                db.collection("users").document(username).update({"profile_pic": None})
                st.success("Profile picture deleted.")

        # Upload Post
        st.subheader("Upload your talent post")
        post_file = st.file_uploader("Image or Video", type=['png','jpg','jpeg','mp4'])
        post_desc = st.text_area("Description (optional)")
        category = st.selectbox("Category", ["General","Singing","Writing","Other"])
        if st.button("Post Talent"):
            if post_file:
                post_data = {
                    "skiller_id": username,
                    "file": post_file.getvalue(),
                    "description": post_desc,
                    "category": category,
                    "timestamp": datetime.now(),
                    "rating": 5  # Admin initial rating
                }
                db.collection("posts").add(post_data)
                st.success("Talent posted with admin rating 5!")

        # Delete post
        st.subheader("Your Posts")
        posts_ref = db.collection("posts").where("skiller_id", "==", username).stream()
        for post in posts_ref:
            post_data = post.to_dict()
            st.write(f"Post ID: {post.id} | Category: {post_data['category']}")
            if post_data.get("description"):
                st.write(post_data["description"])
            if st.button(f"Delete {post.id}"):
                db.collection("posts").document(post.id).delete()
                st.success("Post deleted!")

    elif role=="scout":
        st.header(f"Welcome Scout: {username}")
        category_filter = st.selectbox("Filter by category", ["All","General","Singing","Writing","Other"])
        posts_ref = db.collection("posts").order_by("rating", direction=firestore.Query.DESCENDING).stream()
        for post in posts_ref:
            post_data = post.to_dict()
            if category_filter!="All" and post_data["category"]!=category_filter:
                continue
            st.image(post_data["file"], width=300)
            if post_data.get("description"):
                st.write(post_data["description"])
            rating = st.number_input("Rate this talent", min_value=1, max_value=10, key=post.id)
            if st.button(f"Submit Rating for {post.id}"):
                new_rating = (post_data["rating"] + rating) / 2
                db.collection("posts").document(post.id).update({"rating": new_rating})

    elif role=="admin":
        st.header(f"Welcome Admin: {username}")
        st.subheader("All Users")
        users = db.collection("users").stream()
        for user_doc in users:
            u = user_doc.to_dict()
            st.write(f"{user_doc.id} | Role: {u['role']} | Tokens: {u['tokens']} | Banned: {u.get('banned', False)}")
            if st.button(f"Ban {user_doc.id}"):
                ban_user(user_doc.id)
                st.success(f"{user_doc.id} has been banned.")

        st.subheader("Payment Requests")
        payments = db.collection("payments").stream()
        for pay in payments:
            p = pay.to_dict()
            st.write(f"{p['skiller_id']} requested {p['tokens']} tokens | Amount: {p['amount']}")
            if 'screenshot' in p:
                st.image(p['screenshot'], width=300)
            if st.button(f"Approve {pay.id}"):
                db.collection("users").document(p['skiller_id']).update({"tokens": firestore.Increment(p['tokens'])})
                db.collection("payments").document(pay.id).update({"status":"approved"})
                st.success("Tokens added!")
