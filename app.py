
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# Import your compiled graph
from main import finalgraph

def run_app():


    st.set_page_config(
        page_title="Data Assistant",
        page_icon="🤖",
        layout="wide"
    )


    print("APPLICATION EXECUTED", flush=True)

    if st.button("Test logging"):
        print("BUTTON CLICKED", flush=True)

    st.title("🤖 Data Assistant")
    st.caption("Ask questions about your data or anything else.")

    # Initialize session state
    if "history" not in st.session_state:
        st.session_state.history = []

    if "fullhistory" not in st.session_state:
        st.session_state.fullhistory=[]

    #if "chat_display" not in st.session_state:
    #    st.session_state.chat_display = []

    # Display existing conversation
    #for message in st.session_state.chat_display:
    #     with st.chat_message(message["role"]):
    #        st.markdown(message["content"])

    for message in st.session_state.history:
        if isinstance(message,HumanMessage):
            role="user"
        elif isinstance(message,AIMessage):
            role="assistant"
        else:
            continue
        with st.chat_message(role):
            st.markdown(message.content)

            

    # Chat input
    question = st.chat_input("Ask me anything...")

    if question:

        # Display user question
        #st.session_state.chat_display.append(
        #    {"role": "user", "content": question}
        #)

        with st.chat_message("user"):
            st.markdown(question)

        # Invoke graph
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):

                result = finalgraph.invoke({
                    "user_input": question,
                    "schema": None,
                    "query": None,
                    "export": None,
                    "next_agent": "",
                    "answer": "",
                    "history":st.session_state.fullhistory,
                    "history_to_be_displayed": st.session_state.history
                })

                answer = result["answer"]

                st.markdown(answer)

        # Store display history
        # st.session_state.chat_display.append(
        #     {"role": "assistant", "content": answer}
        # )

        # Store graph history
        st.session_state.history = result["history_to_be_displayed"]

        #Store Full History
        st.session_state.fullhistory = result["history"]

        st.rerun()

run_app()