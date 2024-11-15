import streamlit as st

# Set page configuration
st.set_page_config(page_title="The US House - Mise à Jour", page_icon="🌐", layout="centered")

# Custom CSS styling for centered logo and layout
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f4fa;
        padding: 50px;
        border-radius: 15px;
        max-width: 600px;
        margin: auto;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .logo {
        width: 200px;
        margin: 0 auto;
        display: block;
        border-radius: 10px;
    }
    .header {
        text-align: center;
        font-family: Arial, sans-serif;
        color: #1a1a1a;
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
    }
    .message {
        text-align: center;
        font-size: 18px;
        color: #444444;
        font-family: 'Helvetica', sans-serif;
        margin-top: 20px;
    }
    .link {
        color: #007bff;
        font-weight: bold;
        text-decoration: none;
    }
    .link:hover {
        text-decoration: underline;
    }
    .contact {
        text-align: center;
        font-size: 16px;
        color: #555555;
        margin-top: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Center the logo
st.markdown(
    """
    <div class="main">
        <img src="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=228,fit=crop,q=95/YBgonz9JJqHRMK43/blue-red-minimalist-high-school-logo-9-AVLN0K6MPGFK2QbL.png" class="logo">
    </div>
    """,
    unsafe_allow_html=True,
)

# Display the header message
st.markdown("<h2 class='header'>Nous avons déménagé vers un nouveau site web !</h2>", unsafe_allow_html=True)

# Display the main message
st.markdown(
    """
    <div class='message'>
        Veuillez visiter notre nouveau site et application mis à jour. Connectez-vous avec vos identifiants pour faciliter votre travail :
        <a class='link' href='https://theushouse-partners.replit.app/' target='_blank'>Visitez ici</a>.
    </div>
    """,
    unsafe_allow_html=True,
)

# Display the contact information
st.markdown(
    """
    <div class='contact'>
        The US House Algeria apprécie votre partenariat et est là pour vous aider. <br>
        Si vous avez besoin d'aide, contactez-nous sur WhatsApp.
    </div>
    """,
    unsafe_allow_html=True,
)
