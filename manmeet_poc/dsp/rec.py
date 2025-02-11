import streamlit as st
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import os
import pandas as pd
# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = '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'
# Directories
base_dir = os.getcwd()
my_folder = 'my_folder'
os.makedirs(os.path.join(base_dir, my_folder), exist_ok=True)
# Tabs for Upload and Recommendation
tab1, tab2 = st.tabs([":outbox_tray: Upload Data", ":mag: Get Recommendations"])
# Upload Tab
with tab1:
    st.header("Upload CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            # Save uploaded file
            file_path = os.path.join(base_dir, my_folder, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            # Read CSV
            df = pd.read_csv(file_path)
            # Process data into documents
            data = []
            for i in range(len(df)):
                context = df['qualification'][i]
                caretaker_name = df['caretaker_name'][i]
                caretaker_number = df['caretaker_number'][i]
                doc = Document(page_content=context, metadata={"caretaker_name": caretaker_name, "caretaker_number": caretaker_number})
                data.append(doc)
            # Create embeddings and store in Chroma
            embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
            vectordb = Chroma.from_documents(data, embedding=embeddings, persist_directory='dbb')
            vectordb.persist()
            # Cleanup uploaded file
            os.remove(file_path)
            st.success(f"Successfully uploaded and processed {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error: {e}")
            
with tab2:
    st.header("DSP Recommendation")
    query = st.text_input("Write the patient-related issues here:")

    if "selected_states" not in st.session_state:
        st.session_state.selected_states = []  # Initialize session state for selected buttons

    if st.button("Get Recommendations"):
        if query:
            try:
                # Load vector store and perform similarity search
                embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
                vectordb = Chroma(persist_directory="dbb", embedding_function=embeddings)
                results = vectordb.similarity_search_with_score(query, k=5)
                
                # Ensure session state is initialized for the current results
                if not st.session_state.selected_states or len(st.session_state.selected_states) != len(results):
                    st.session_state.selected_states = [False] * len(results)

                # Extract caretaker names from results
                caretaker_names = [doc.metadata['caretaker_name'] for doc, _ in results]

                # Display all caretaker names in vertical format
                st.subheader("Recommended Caretakers:")
                for name in caretaker_names:
                    st.write(f"- {name}")
                
                # Add another heading with two fake names
                st.subheader("Other Caretakers:")
                st.write("- Alex Johnson")
                st.write("- Emma Davis")
                
                # Display detailed recommendations with 'Select' button functionality
                st.subheader("Recommendations:")
                for i, (doc, score) in enumerate(results):
                    with st.expander(f"### Recommendation {i+1}", expanded=False):
                        st.write(f"**Caretaker Name:** {doc.metadata['caretaker_name']}")
                        st.write(f"**Qualification:** {doc.page_content}")
                        st.write("---")
                        
                        button_html = f"""
                        <button onclick="alert('Selected')"
                                style="background-color:#4CAF50; color:white; padding:10px 15px; border:none; border-radius:5px; cursor:pointer;">
                            Select
                        </button>
                        """
                        st.markdown(button_html, unsafe_allow_html=True)
                        

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a query.")
    
    st.write("### Thank You for Using Our Application")
    image_path = "image.jpeg"  # Replace with the actual path to your image
    if os.path.exists(image_path):
        st.image(image_path, caption="Powered by DSP AI")
    else:
        st.warning("Static image file not found. Please make sure the image file is in the correct location.")