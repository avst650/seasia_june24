import streamlit as st
from Questions import response
st.title("Must Ask Reference Check Questions")
# print(response['technical_questions'])
res = response['general_questions']
for i in res:
    st.write(i)

