from langchain_openai import ChatOpenAI


def pick_llm(model):
    # 1. Initialize the LLM
    if model=="high":
        llm = ChatOpenAI(model="gpt-6.1-sol")
    elif model=="medium":
        llm = ChatOpenAI(model="gpt-6-luna")
    else:
        llm = ChatOpenAI(model="gpt-4.1") 

    return llm

