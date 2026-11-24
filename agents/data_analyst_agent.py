import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tools.data_analyst_tools import exec_query,get_schema
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


load_dotenv()
#Define model

def data_analyst_agent():
    # 1. Initialize the LLM
    system_prompt="""
    You are an expert Data Analyst Agent.

        Your responsibility is to answer questions involving
        business data, SQL queries and data analysis.

        Rules:

        1. Use the available tools to retrieve and analyze data.

        2. If you can answer the question using the database,
           available tools or conversation history, answer the user.

        3. If a SQL query fails, attempt to correct it when possible.

        4. If the request is unrelated to data analysis, or you
           cannot answer the request using your available data,
           tools or capabilities, call handoff_to_supervisor
           explaining why.

        5. Do not call handoff_to_supervisor merely because
           a SQL query initially fails.

        6. Do not fabricate data.
        """
    llm = ChatOpenAI(model="gpt-6-luna")
    data_analyst_agent=create_agent(model=llm,
                                    tools=[get_schema,exec_query],
                                    system_prompt=system_prompt
                                    )

    return data_analyst_agent


