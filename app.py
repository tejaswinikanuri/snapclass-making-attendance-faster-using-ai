import streamlit as st

def main():
    st.header("This is title")
    name = st.text_input("enter name")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("greet", type="secondary", key="greet", width="stretch"):
            st.header(f"hi {name}")

    with col2:
        if st.button("bye", type="secondary", key="bye", width="stretch"):
            st.header(f"bye {name}")

    st.markdown("""
        <style>
        button {
            background-color:blue !important;
        }
        </style>

    """, unsafe_allow_html=True)

main()

