from typing import TypedDict, Literal, Optional
from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
from agents.data_analyst_agent import data_analyst_agent
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
from langgraph.types import interrupt
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.data_analyst_validator_tools import get_schema
from tools.pick_llm import pick_llm


load_dotenv()

class SupervisorDecision(BaseModel):
    next_agent:Literal[
        "data_analyst_validator",
        "direct"
    ]

class DataAnalystValidatorDecision(BaseModel):
    status: Literal["clear","clarification_required"]
    clarification_question:str

# 1. Define the Graph State
class ComparisonState(TypedDict):
    user_input: str
    schema: Optional[str]
    query: Optional[str]
    export: Optional[str]
    next_agent: str
    answer: str
    history: list
    status: Optional[str]
    clarification_question:Optional[str]


# 3. Supervisor Node
def supervisor(state: ComparisonState)->ComparisonState:
    messages=state["history"]+[HumanMessage(content=state["user_input"])]

    history_text = "\n".join(
    f"\n{msg.type}: {msg.content}"
    for msg in messages)

    #print(f"History:\n{history_text}")

    prompt = f"""
    You are a Supervisor Agent.

    Analyze the user's input and history select exactly one route:

    - data_analyst_validator: Questions involving database queries,
      calculations, data analysis or business data.

    - direct: Greetings, general questions, explanations
      or requests that don't require data analysis or reporting.

    User Input:
    {state["user_input"]}

    Conversation History:
    {history_text}

    Respond with ONLY one of these values:
    data_analyst_validator
    direct
    """

    print("\n===============================Invocation of Supervisor in progress=======================================\n")
    llm = pick_llm("medium")
    result = llm.with_structured_output(SupervisorDecision).invoke(prompt)
    

    state["next_agent"] = result.next_agent.strip().lower()
    

    return state


def data_analyst_validator(state:ComparisonState)->ComparisonState:
    schema=get_schema()
    messages = state["history"] +  [HumanMessage(content=state["user_input"])]

    history_text = "\n".join(
        f"\n{msg.type}: {msg.content}"
        for msg in messages)
    
    # 1. Initialize the LLM
    system_prompt = f"""
    You are an expert Data Analyst Validator Agent.

    Your responsibility is to evaluate whether the user's question
    is sufficiently clear to perform accurate business data analysis.

    You will be provided with the user's question, relevant database
    schema, business definitions and conversation history.

    Rules:

    1. If the user's question is clear and can be interpreted
    without making assumptions, respond with exactly:
    clear

    2. If the user's question is ambiguous, lacks essential context,
    or requires clarification, respond with:
    clarification_required: <specific clarification question>

    3. Ask only one specific clarification question at a time.

    4. Do not request information that is already available
    in the database schema, business definitions or conversation history.

    5. Do not make assumptions about business metrics, date ranges,
    filters or dimensions when they materially affect the result.

    6. Do not generate SQL queries or execute database tools.
    Your only responsibility is question validation.

    Use schema
    {schema}

    Conversation History 
    {history_text}


    """

    llm = ChatOpenAI(model="gpt-4.1")

    data_analyst_validator=llm.with_structured_output(DataAnalystValidatorDecision)


    print("\n===============================Invocation of Data Analyst Validator in progress=======================================\n")
    decision = data_analyst_validator.invoke([
    SystemMessage(content=system_prompt),
    HumanMessage(content=state["user_input"])
    ])

    print("\n==============================Decision by Data Analyst Validator======================================================\n")
    state["status"]=decision.status
    state["clarification_question"]=decision.clarification_question

    print(f"State:{state["status"]}")
    print(f"Clarification Question:{state["clarification_question"]}")

    if state["status"]=="clarification_required":
        
        # user_clarification = interrupt(
        #     state["clarification_question"]
        # )
        
        # state["user_input"] = (
        #     state["user_input"]
        #     + "\nUser clarification: "
        #     + user_clarification)
        state["answer"]=state["clarification_question"]
        state["history"]=messages+[AIMessage(content=state["clarification_question"])]

    else:
        print("...............................Clear Passing to Data Analyst.......................................................")    
    
    return state

def data_analyst(state:ComparisonState)->ComparisonState:
    agent=data_analyst_agent()

    messages = state["history"] +  [HumanMessage(content=state["user_input"])]
    
    data_analyst_response=agent.invoke({"messages":messages})

    print("\n============================Invocation of Data Analyst in progress================================\n")

    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0
    llm_call_no = 0
    final_query=""
    
    for msg in data_analyst_response["messages"]:

        if isinstance(msg, AIMessage) and msg.usage_metadata:

            llm_call_no += 1
            usage = msg.usage_metadata
            input_tokens = usage["input_tokens"]
            output_tokens = usage["output_tokens"]
            call_total = usage["total_tokens"]

            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_tokens += call_total
            
            if msg.tool_calls:
                for tool in msg.tool_calls:
                    print("TOOL CALL:", tool["name"])
                    if tool["name"]=="exec_query":
                        print("TOOL ARGS:",tool["args"]["query"]) 
                        final_query=tool["args"]["query"]
                   
            else:
                print(f"\nLLM Call #{llm_call_no} | Final/Normal Response") 

            print("Input Tokens:", input_tokens)
            print("Output Tokens:", output_tokens)
            print("Total Tokens:", call_total)

        elif msg.type=="tool":
            if msg.name == "get_schema":
                print(f"Tool Value:\n{msg.content}")

    print("\n========== GRAND TOTAL FOR DATA ANALYST AGENT==========\n")
    print("Total Input Tokens:", total_input_tokens)
    print("Total Output Tokens:", total_output_tokens)
    print("Total Tokens Consumed:", total_tokens)

    state["query"]=final_query
    
    state["answer"]=data_analyst_response["messages"][-1].content[-1]["text"]
    state["history"]=messages+[AIMessage(content=data_analyst_response["messages"][-1].content[-1]["text"])]

    datanalysthistory = "\n".join(
            f"\n{msg.type}: {msg.content}"
            for msg in state["history"])
    
    print(f"\n=============================Data Analyst History===========================\n{datanalysthistory}")

    #print(f"\n===========================Non Cleaned Data Analyst History===========================\n{state["history"]}")


    return state

# 5. Direct Response Node
def direct(state: ComparisonState)->ComparisonState:
    messages = state["history"] + [
        HumanMessage(content=state["user_input"])
    ]

    llm=pick_llm("low")
    response = llm.invoke(messages)

    print("\n===============================Invocation of Direct Analyst in progress=================================\n")
    msg=response.usage_metadata
    input_tokens=msg["input_tokens"]
    output_tokens=msg["output_tokens"]
    total_tokens=msg["total_tokens"]

    print("\n========== GRAND TOTAL FOR DIRECT AGENT==========\n")
    print("Total Input Tokens:", input_tokens)
    print("Total Output Tokens:", output_tokens)
    print("Total Tokens Consumed:", total_tokens)

    state["answer"]=response.content
    state["history"]  = messages + [AIMessage(content=response.content)]


    directhistory = "\n".join(
            f"\n{msg.type}: {msg.content}"
            for msg in state["history"])
    
    print(f"\n=================================Direct History====================================\n{directhistory}")

    #print(f"\n============================Non Cleaned Direct History==============================\n{state["history"]}")

    return state

def route_supervisor(state:ComparisonState):
    return state["next_agent"]

def route_data_analyst_validator(state:ComparisonState):
    if state["status"]=="clarification_required":
        return END
    else:
        return "data_analyst"


# 6. Build the Graph
graph = StateGraph(ComparisonState)

#7. Create Nodes
graph.add_node("supervisor", supervisor)
graph.add_node("data_analyst_validator", data_analyst_validator)
graph.add_node("data_analyst", data_analyst)
graph.add_node("direct", direct)

#Create Edges
graph.add_edge(START, "supervisor")

graph.add_conditional_edges("supervisor",route_supervisor,{"data_analyst_validator":"data_analyst_validator","direct":"direct"})
graph.add_conditional_edges("data_analyst_validator",route_data_analyst_validator,{"data_analyst":"data_analyst",END:END})

#graph.add_edge("data_analyst_validator", "data_analyst")
graph.add_edge("data_analyst", END)
graph.add_edge("direct", END)

# 7. Compile the Graph
finalgraph = graph.compile()


png_data = finalgraph.get_graph().draw_mermaid_png()

with open("graph.png", "wb") as f:
    f.write(png_data)