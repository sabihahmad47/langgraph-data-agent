# Import your compiled graph
from main import finalgraph


while True:
    question=input("Ask any business question or exit:")
    if question=="exit":
        break
    else:
        history=[]
        history_to_be_displayed=[]
        result = finalgraph.invoke({
                            "user_input": question,
                            "schema": None,
                            "query": None,
                            "export": None,
                            "next_agent": "",
                            "answer": "",
                            "history":history,
                            "history_to_be_displayed": history_to_be_displayed
                        })

        history_to_be_displayed=result["history_to_be_displayed"]
        history=result["history"]
