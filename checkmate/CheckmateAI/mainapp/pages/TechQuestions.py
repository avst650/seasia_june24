import streamlit as st
from Questions import response
st.title("Technical Questions")
# print(response['technical_questions'])
res = response['technical_questions']
for i in res:
    st.write(i)

