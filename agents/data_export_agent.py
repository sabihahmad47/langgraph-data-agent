from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tools.data_export_tools import export_result
from dotenv import load_dotenv

load_dotenv()
#Define model

def data_export_agent():
        
    # 1. Initialize the LLM
    llm = ChatOpenAI(model="gpt-6-luna")

    data_export_agent=create_agent(model=llm,
                                    tools=[export_result],
                                    system_prompt="""You are an expert Data Export Agent. Export the results. Use tools to answer business questions if necessary."""
                                    )

    return data_export_agent