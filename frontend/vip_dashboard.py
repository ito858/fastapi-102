# vip_dashboard.py
from pydantic import BaseModel
from typing import Optional
import decimal
from datetime import datetime
import streamlit as st

import barcode
from barcode.writer import ImageWriter
from io import BytesIO


# VIP BaseModel
class VIP(BaseModel):
    IDvip: int
    code: Optional[str] = None
    nascita: Optional[str] = None
    cellulare: Optional[str] = None
    sms: bool = False
    Punti: Optional[int] = None
    Sconto: Optional[int] = None
    Ck: Optional[str] = None
    idata: Optional[datetime] = None
    ioperatore: Optional[int] = None
    inegozio: Optional[int] = None
    P_cs: int = 0
    P_ldata: Optional[str] = None
    P_importo: decimal.Decimal = decimal.Decimal("0.00")
    Nome: Optional[str] = None
    Indirizzo: Optional[str] = None
    Cap: Optional[str] = None
    Citta: Optional[str] = None
    Prov: Optional[str] = None
    CodiceFiscale: Optional[str] = None
    PartitaIva: Optional[str] = None
    Email: Optional[str] = None
    sesso: int = 0
    VIPanno: int = 0
    maps: Optional[str] = None
    VIPscadenza: Optional[str] = None
    Blocco: int = 0
    cognome: str = ""
    SerBlocco: int = 0
    SerBloccoBz: str = ""
    omail: bool = False
    oposte: bool = False
    msg: int = 0
    msgstr: str = ""
    utime: str = ""
    upc: str = ""
    uzt: int = 0
    un: str = ""
    lotteria: str = ""
    statoanno: str = ""
    img: Optional[bytes] = None
    n: str = ""
    SCOscadenza: str = ""

# Section Functions
def display_personal_info(vip: VIP):
    st.header("Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {vip.Nome or 'N/A'} {vip.cognome}")
        st.write(f"**Tax Code:** {vip.CodiceFiscale or 'N/A'}")
    with col2:
        st.write(f"**Birth Date:** {vip.nascita or 'N/A'}")
        st.write(f"**Gender:** {'Unspecified' if vip.sesso == 0 else 'Male' if vip.sesso == 1 else 'Female'}")

def display_membership_details(vip: VIP):
    st.header("Membership Details")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**VIP ID:** {vip.IDvip}")
        st.write(f"**Membership Year:** {vip.VIPanno or 'N/A'}")
    with col2:
        st.write(f"**Expiration Date:** {vip.VIPscadenza or 'N/A'}")
        st.write(f"**Status:** {'Active' if vip.Blocco == 0 else 'Blocked'}")

def display_points_discounts(vip: VIP):
    st.header("Points & Discounts")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Points:** {vip.Punti or 0}")
        st.write(f"**Last Points Update:** {vip.P_ldata or 'N/A'}")
    with col2:
        st.write(f"**Discount:** {vip.Sconto or 0}%")
        st.write(f"**Total Spent:** {vip.P_importo} €")

def display_contact_info(vip: VIP):
    st.header("Contact Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Phone:** {vip.cellulare or 'N/A'}")
        st.write(f"**Email:** {vip.Email or 'N/A'}")
        st.write(f"**SMS Opt-in:** {'Yes' if vip.sms else 'No'}")
        st.write(f"**Email Opt-in:** {'Yes' if vip.omail else 'No'}")
    with col2:
        st.write(f"**Address:** {vip.Indirizzo or 'N/A'}")
        st.write(f"**City:** {vip.Citta or 'N/A'} ({vip.Cap or 'N/A'})")
        st.write(f"**Province:** {vip.Prov or 'N/A'}")


def display_barcode(vip: VIP):
    st.header("Barcode")
    if vip.code:
        try:
            st.write("Debug: Importing barcode modules...")
            import barcode
            from barcode.writer import ImageWriter
            st.write("Debug: Modules imported successfully")
            code128 = barcode.get_barcode_class('code128')
            st.write("Debug: Barcode class loaded")
            barcode_instance = code128(vip.code, writer=ImageWriter())
            st.write("Debug: Barcode instance created")
            buffer = BytesIO()
            barcode_instance.write(buffer)
            buffer.seek(0)
            st.image(buffer.getvalue(), caption=f"Barcode for {vip.code}")
        except Exception as e:
            st.error(f"Failed to generate barcode: {e}")
    else:
        st.write("No barcode available (VIP code missing)")

def display_dashboard(vip: VIP):
    """Main function to display the full VIP dashboard."""
    st.title("VIP Membership Dashboard")
    display_personal_info(vip)
    display_membership_details(vip)
    display_points_discounts(vip)
    display_contact_info(vip)
    display_barcode(vip)  # Replace the old barcode request block
#     display_profile_image(vip)
    st.write("---")
    st.write(f"Last updated: {vip.utime or 'Not available'}")


