import streamlit as st
from Questions import response
st.title("Reference Check Questions for the person referning the candidate")
# print(response['technical_questions'])
res = response['reference_questions']
for i in res:
    st.write(i)

