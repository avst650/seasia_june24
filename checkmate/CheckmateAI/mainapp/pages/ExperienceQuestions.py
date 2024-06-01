import streamlit as st
from Questions import response
st.title("Reference Check Question Related to Experience")
# print(response['technical_questions'])
res = response['experience_questions']
for i in res:
    st.write(i)

