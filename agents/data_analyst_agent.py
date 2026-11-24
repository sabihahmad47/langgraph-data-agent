import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tools.data_analyst_tools import exec_query,get_schema
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from tools.pick_llm import pick_llm

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

        4. If the user's question is clear answer the question

        5. If the user's question is ambiguous, lacks sufficient context, or requires clarification before performing the analysis REPOND with "clarification_required"
        """
    llm = pick_llm("medium")
    data_analyst_agent=create_agent(model=llm,
                                    tools=[get_schema,exec_query],
                                    system_prompt=system_prompt
                                    )

    return data_analyst_agent


