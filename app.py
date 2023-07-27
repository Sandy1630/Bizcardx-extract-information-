import easyocr
import pandas as pd
import streamlit as st
import numpy as np
from PIL import Image
import re
import sqlite3
from streamlit_option_menu import option_menu

sandy=sqlite3.connect("bizcard.db")
cur=sandy.cursor()
reader=easyocr.Reader(["en"],gpu=False)

st.set_page_config(page_title="BizCardX: Extracting Business Card Data with OCR", page_icon="random", layout="wide", initial_sidebar_state="auto", menu_items=None)
st.title("BizCard")





def data_extrac(extract):
    for i in range(len(extract)):
        extract[i] = extract[i].rstrip(' ')
        extract[i] = extract[i].rstrip(',')
    result = ' '.join(extract)

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    website_pattern = r'[www|WWW|wwW]+[\.|\s]+[a-zA-Z0-9]+[\.|\][a-zA-Z]+'
    phone_pattern = r'(?:\+)?\d{3}-\d{3}-\d{4}'
    phone_pattern2 = r"(?:\+91[-\s])?(?:\d{4,5}[-\s])?\d{3}[-\s]?\d{4}"
    name_pattern = r'[A-Za-z]+\b'
    designation_pattern = r'\b[A-Za-z\s]+\b'
    address_pattern = r'\d+\s[A-Za-z\s,]+'
    pincode_pattern = r'\b\d{6}\b'

    name = designation = company = email = website = primary = secondary = address = pincode = None

    try:
        email = re.findall(email_pattern, result)[0]
        result = result.replace(email, '')
        email = email.lower()
    except IndexError:
        email = None
    try:
        website = re.findall(website_pattern, result)[0]
        result = result.replace(website, '')
        website = re.sub('[WWW|www|wwW]+ ', 'www.', website)
        website = website.lower()
    except IndexError:
        webstie = None
    phone = re.findall(phone_pattern, result)
    if len(phone) == 0:
        phone = re.findall(phone_pattern2, result)
    primary = None
    secondary = None
    if len(phone) > 1:
        primary = phone[0]
        secondary = phone[1]
        for i in range(len(phone)):
            result = result.replace(phone[i], '')
    elif len(phone) == 1:
        primary = phone[0]
        result = result.replace(phone[0], '')

    try:
        pincode = int(re.findall(pincode_pattern, result)[0])
        result = result.replace(str(pincode), '')
    except:
        pincode = 0
    # name = re.findall(name_pattern, result)[0]
    name = extract[0]
    result = result.replace(name, '')
    # designation = re.findall(designation_pattern, result)[0]
    designation = extract[1]
    result = result.replace(designation, '')
    address = ''.join(re.findall(address_pattern, result))
    result = result.replace(address, '')
    company = extract[-1]
    result = result.replace(company, '')

    # print('Email:', email)
    # print('Website:', website)
    # print('Phone:', phone)
    # print('Primary:', primary)
    # print('Secondary:', secondary)
    # print('Name:', name)
    # print('Designation:', designation)
    # print('Address:', address)
    # print('Pincode:', pincode)
    # print('company:', company)
    # print('remaining:', result)

    info = [name, designation, company, email, website, primary, secondary, address, pincode, result]
    return (info)


with st.sidebar:
  selected=option_menu("main menu",["Home","Upload","View/Modify","About"],icons=["house","upload","binoculars","envelope"],menu_icon="person-vcard")
  selected
if selected=="Home":
  st.subheader("Welcome to the Bizcard Project!")
  st.markdown("__<p>We are here to introduce you to an innovative solution that will transform the way you manage "
                "your contact information. Our project is centered around simplifying the process of storing and "
                "accessing business cards by creating a digital database.</p>__ "
                "<br>"
                "__<p>Gone are the days of manually entering contact details from visiting cards. "
                "With our cutting-edge technology, all you need to do is scan the card using our integrated scanner, "
                "and voila! A soft copy of the card is created and securely stored in our database.</p>__ "
                "<br>"
                "__<p>Imagine the convenience of having all your contacts readily available at your fingertips. "
                "No more digging through stacks of business cards or struggling to remember where you put that "
                "important contact. Our system ensures that your contacts are organized and easily searchable, "
                "saving you time and effort.</p>__"
                "<br>"
                "__<p>Not only does our BizCard Project offer a streamlined approach to managing contacts, "
                "but it eliminating the need for physical storage and "
                "reducing the risk of losing important cards, our digital database ensures that your valuable "
                "connections are preserved for the long term.</p>__ "
                "<br>"
                "__<p>We understand the importance of building and nurturing relationships in the business world. "
                "That's why our project empowers you to strengthen your network efficiently. With quick access to "
                "contact information, you can reach out to potential clients, collaborators, or partners effortlessly, "
                "helping you seize every opportunity that comes your way.</p>__ "
                "<br>"
                "__<p>Join us on this journey of revolutionizing contact management. Say goodbye to cluttered desks "
                "and hello to a digital future. Explore our BizCard Project and discover the ease and efficiency of "
                "keeping your contacts in a secure, accessible, and organized format. </p>__"
                "<br>"
                "__<p>Start scanning, start connecting, and start building lasting relationships with the BizCard "
                "Project.</p>__",unsafe_allow_html=True)




if selected=="Upload":
  file_uploader=st.file_uploader("select image file",type=["png","jpg","jpeg"])
  if file_uploader is not None:
    image=Image.open(file_uploader)
    col2,col3=st.columns(2)
    with col3:
     st.image(image)
    with col2:
     if image is not None:
      result=reader.readtext(np.array(image),detail=0)
      info=data_extrac(result)
      f_name=st.text_input("Name :",info[0])
      f_designation=st.text_input("Designation :",info[1])
      f_company=st.text_input("Company :",info[2])
      f_email=st.text_input("Email id :",info[3])
      f_website=st.text_input("Website :",info[4])
      f_primary=st.text_input("Primary_number :",info[5])
      f_secondary=st.text_input("Secondary_number :",info[6])
      f_address=st.text_input("Address :",info[7])
      f_pincode=st.text_input("Pincode :",info[8])
      a=st.button("upload")
      if a:
        cur.execute("""create table if not exists business_cards(Name varchar(255),Designation varchar(255),
        Company varchar(255),Email varchar(255),Website varchar(255),Primary_number varchar(255),
        Secondary_number varchar(255),
        Address varchar(255),Pincode int)""")
        query="""insert into business_cards(Name,Designation,Company,Email,Website,Primary_number,
        Secondary_number,Address,Pincode)
        values(?,?,?,?,?,?,?,?,?)"""
        val=(f_name,f_designation,f_company,f_email,f_website,f_primary,f_secondary,f_address,f_pincode)
        cur.execute(query,val)
        sandy.commit()
        st.success("Contact stored in Database",icon="✅")
if selected=="View/Modify":
  col1,col2,col3=st.columns(3)
  with col1:
    cur.execute("select name from business_cards")
    y=cur.fetchall()
    contact=[x[0] for x in y]
    contact.sort()
    selected_contact=st.selectbox("Name",contact)
  with col2:
    mode_list=["view","modify","delete"]
    selected_mode=st.selectbox("mode",mode_list,index=0)

  if selected_mode=="view":
    col5,col6=st.columns(2)
    with col5:
      cur.execute(f'''select Name,Designation,Company,Email,Website,Primary_number,Secondary_number,
      Address,Pincode from business_cards where Name="{selected_contact}"''')
      y=cur.fetchall()
      st.table(pd.Series(y[0],index=["Name","Designation","Company","Email","Company",
                                     "Primary_number","Secondary_number","Address","Pincode"],name="card_info"))
  if selected_mode=="modify":
    cur.execute(f"""select Name,Designation,Company,Email,Website,Primary_number,Secondary_number,
    Address,Pincode from business_cards where Name='{selected_contact}'""")
    info=cur.fetchone()
    col5,col6=st.columns(2)
    with col5:
      f_name=st.text_input("Name :",info[0])
      f_designation=st.text_input("Designation :",info[1])
      f_company=st.text_input("Company :",info[2])
      f_email=st.text_input("Email id :",info[3])
      f_website=st.text_input("Website :",info[4])
      f_primary=st.text_input("Primary_number :",info[5])
      f_secondary=st.text_input("Secondary_number :",info[6])
      f_address=st.text_input("Address :",info[7])
      f_pincode=st.text_input("Pincode :",info[8])
    a=st.button("update")
    if a:
      query=f'''update business_cards set Name=?,Designation=?,Company=?,Email=?,Website=?,
      Primary_number=?,Secondary_number=?,Address=?,Pincode=? where Name="{selected_contact}"'''
      val=(f_name,f_designation,f_company,f_email,f_website,f_primary,f_secondary,f_address,f_pincode)
      cur.execute(query,val)
      sandy.commit()
      st.success("contact updated sucessfully in database",icon="✅")
  if selected_mode=="delete":
    st.markdown(
            f'__<p style="text-align:left; font-size: 20px; color: #FAA026">You are trying to remove {selected_contact} '
            f'contact from database.</P>__',
            unsafe_allow_html=True)
    warning_content = """
            **Warning:**
            This action will permanently delete the contact from the database and cannot be recovered. 
            Please review and confirm..
        """
    st.warning(warning_content)
    confirm = st.button('Confirm')
    if confirm:
      query = f"DELETE FROM business_cards where name = '{selected_contact}'"
      cur.execute(query)
      sandy.commit()
      st.success('Contact removed successfully from database', icon="✅")
elif selected == 'About':
  st.markdown('__<p style="text-align:left; font-size: 25px; color: #FAA026">Summary of BizCard Project</P>__',
                unsafe_allow_html=True)
  st.write("This business card project focused on enabling users to scan any visiting card and make a soft copy in "
             "the database. This innovative business card project has revolutionized the way we store contact "
             "information. With its built-in scanner, users can quickly and easily scan any visiting card into a "
             "soft copy, which can be stored in a secure database for quick access. This is an efficient and effective "
             "way to keep track of contacts and build relationships.")
  st.markdown('__<p style="text-align:left; font-size: 20px; color: #FAA026">Applications and Packages Used:</P>__',
                    unsafe_allow_html=True)
  st.write("  * Python")
  st.write("  * sqlite3")
  st.write("  * Streamlit")
  st.write("  * Github")
  st.write("  * Pandas, EasyOCR, Re, image, sqlite3")
  st.markdown('__<p style="text-align:left; font-size: 20px; color: #FAA026">For feedback/suggestion, connect with me on</P>__',
                unsafe_allow_html=True)
  st.subheader("Email ID")
  st.write("santhoshkumar.e2000@gmail.com")
  st.subheader("Github")
  st.write("https://github.com/Sandy1630")
  st.balloons()













