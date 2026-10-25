
import os
from typing import TypedDict

# LangGraph components:
# StateGraph -> Creates the workflow graph.
# END -> Special marker that tells LangGraph to stop execution.
from langgraph.graph import END, StateGraph

# Loads environment variables from the .env file.
from dotenv import load_dotenv

# Groq SDK to communicate with the LLM.
from groq import Groq


# ============================================================
# 1. ENVIRONMENT SETUP
# ============================================================

# Load variables stored in the .env file.
# Example: GROQ_API_KEY=your_api_key
load_dotenv()

# Read the Groq API key from environment variables.
my_api_key = os.getenv("GROQ_API_KEY")

# Stop execution if the API key is missing.
if not my_api_key:
    raise ValueError("API key kaha hai bhai")

# Create the Groq client to send requests to the LLM.
client = Groq(api_key=my_api_key)

# Name of the LLM model used for all AI requests.
groqmodel = "openai/gpt-oss-120b"


# ============================================================
# 2. SHARED STATE
# ============================================================

# State stores the information shared between graph nodes.
# Each node receives the current state and returns updates.
class State(TypedDict):
    query: str    # Original user query, updated if clarification is needed.
    order: str    # Extracted order that will be prepared and served.
    proceed: bool # True/False decision used by conditional routing.


# ============================================================
# 3. HELPER FUNCTION: ASK THE LLM
# ============================================================

def ask_llm(prompt: str) -> bool:
    """
    Sends a prompt to the Groq LLM and converts its answer
    into a Python boolean.

    Used by validation and cooking nodes to make decisions.
    Expected LLM output: TRUE or FALSE.
    """

    response = client.chat.completions.create(
        model=groqmodel,
        messages=[
            # Instruct the model to provide a boolean-style answer.
            {"role": "system", "content": "Answer only TRUE or FALSE."},

            # The actual question or decision prompt.
            {"role": "user", "content": prompt}
        ],
        temperature=0  # Reduces randomness for more consistent decisions.
    )

    # Extract the model's response, remove extra spaces,
    # and convert it to uppercase for comparison.
    answer = response.choices[0].message.content.strip().upper()

    print("LLM decision:", answer)

    # Convert the text response into a Python boolean.
    # Note: startswith("TRUE") is a simple check, not strict validation.
    return answer.startswith("TRUE")


# ============================================================
# 4. NODE 1: VALIDATE USER QUERY
# ============================================================

def validate_query(state: State) -> dict:
    """
    Checks whether the user's request is related to ordering
    food or beverages from a restaurant.

    If TRUE  -> route to take_order.
    If FALSE -> terminate the workflow.
    """

    # Read the user's current query from the shared state.
    query = state["query"]

    print("\n--- VALIDATE QUERY ---")
    print("User:", query)

    # Ask the LLM whether the request belongs to the restaurant
    # ordering workflow.
    result = ask_llm(
        f"""
        Is this a reasonable restaurant food-ordering request?
        Reject unrelated requests.

        User query: {query}
        Return TRUE or FALSE.
        """
    )

    # Update the shared state.
    # The routing function will use 'proceed' to choose the next node.
    return {"proceed": result}


# ============================================================
# 5. NODE 2: TAKE ORDER
# ============================================================

def take_order(state: State) -> dict:
    """
    Extracts the food items and quantities from the user's query.

    If the quantity is missing, asks the user for clarification.
    Stores the resulting order in the shared state.
    """

    print("\n--- TAKE ORDER ---")

    # Ask the LLM to extract the order or ask a follow-up question
    # if important information, such as quantity, is missing.
    response = client.chat.completions.create(
        model=groqmodel,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a restaurant order-taking assistant. "
                    "Extract food items and quantities. "
                    "If quantity is missing, ask the customer how many. "
                    "If the customer provides a quantity, create a "
                    "complete order summary."
                )
            },
            {
                # Send the current query from the shared state.
                "role": "user",
                "content": state["query"]
            }
        ],
        temperature=0
    )

    # Get the extracted order or clarification question.
    order = response.choices[0].message.content.strip()
    print("Order:", order)

    # Simple check: determine whether the model appears to be asking
    # a follow-up question. This is a beginner-friendly heuristic.
    if "how many" in order.lower() or "?" in order:

        # Pause the workflow and ask the actual user for an answer.
        answer = input("Restaurant Agent: " + order + "\nYou: ")

        # Add the answer to the existing query so that the next node
        # can access the additional information.
        updated_query = state["query"] + ", " + answer

        # Save the updated query and order.
        # Set proceed=True to route directly to cook_order.
        return {
            "query": updated_query,
            "order": updated_query,
            "proceed": True
        }

    # If no clarification seems necessary, save the extracted order.
    # The graph will move to cook_order because proceed=True.
    return {
        "order": order,
        "proceed": True
    }


# ============================================================
# 6. NODE 3: COOK ORDER
# ============================================================

def cook_order(state: State) -> dict:
    """
    Simulates the kitchen preparation stage.

    The LLM checks whether the order is reasonably feasible.
    This does not actually cook food; it is a simulation.

    If TRUE  -> route to serve_order.
    If FALSE -> route back to take_order.
    """

    print("\n--- COOK ORDER ---")

    # Display the order received from the previous node.
    print("Preparing:", state["order"])

    # Ask the LLM whether the kitchen could reasonably prepare it.
    result = ask_llm(
        f"""
        Check whether this is a valid, reasonably prepared
        restaurant order.

        Return TRUE if the kitchen can prepare it.
        Return FALSE if the order is unclear or infeasible.

        Order: {state['order']}
        """
    )

    # Display the simulated preparation result.
    if result:
        print("Cooking completed (simulation).")
    else:
        print("Cooking unsuccessful. Returning to take order.")

    # Update the decision in shared state.
    # The conditional routing function uses this boolean.
    return {"proceed": result}


# ============================================================
# 7. NODE 4: SERVE ORDER
# ============================================================

def serve_order(state: State) -> dict:
    """
    Simulates serving the completed order to the customer.

    In this version, serving always succeeds.
    A real application could update the order status in a database.
    """

    print("\n--- SERVE ORDER ---")

    # Display the order being served.
    print("Serving:", state["order"])

    # Simulate successful serving.
    print("Order served successfully!")

    # Set proceed=True so the graph routes to END.
    return {"proceed": True}


# ============================================================
# 8. CONDITIONAL ROUTING FUNCTIONS
# ============================================================

# Routing functions do not perform the actual restaurant tasks.
# They only decide which node should execute next.


def query_decision(state: State) -> str:
    """
    Called after validate_query.

    TRUE  -> take_order
    FALSE -> end the workflow
    """

    if state["proceed"]:
        return "take_order"

    return "end"


def order_decision(state: State) -> str:
    """
    Called after take_order.

    TRUE  -> cook_order
    FALSE -> validate_query

    Note: the current take_order function always returns TRUE,
    so the FALSE route is not normally used.
    """

    if state["proceed"]:
        return "cook_order"

    return "validate_query"


def cook_decision(state: State) -> str:
    """
    Called after cook_order.

    TRUE  -> serve_order
    FALSE -> take_order to review the order again
    """

    if state["proceed"]:
        return "serve_order"

    return "take_order"


def serve_decision(state: State) -> str:
    """
    Called after serve_order.

    TRUE  -> end the workflow
    FALSE -> return to cook_order

    Note: the current serve_order function always returns TRUE.
    """

    if state["proceed"]:
        return "end"

    return "cook_order"


# ============================================================
# 9. BUILD THE LANGGRAPH WORKFLOW
# ============================================================

# Create a graph that uses our State structure.
builder = StateGraph(State)

# Register the node names and their corresponding functions.
builder.add_node("validate_query", validate_query)
builder.add_node("take_order", take_order)
builder.add_node("cook_order", cook_order)
builder.add_node("serve_order", serve_order)

# Set the first node that executes when the graph starts.
builder.set_entry_point("validate_query")


# ------------------------------------------------------------
# Conditional edges: validate_query -> next node
# ------------------------------------------------------------

builder.add_conditional_edges(
    "validate_query",  # Node that finishes first
    query_decision,    # Function that selects the next destination
    {
        "take_order": "take_order", # If valid, begin order-taking.
        "end": END                  # If invalid, stop the graph.
    }
)


# ------------------------------------------------------------
# Conditional edges: take_order -> next node
# ------------------------------------------------------------

builder.add_conditional_edges(
    "take_order",
    order_decision,
    {
        "cook_order": "cook_order",       # Order is ready for preparation.
        "validate_query": "validate_query" # Revalidate if not ready.
    }
)


# ------------------------------------------------------------
# Conditional edges: cook_order -> next node
# ------------------------------------------------------------

builder.add_conditional_edges(
    "cook_order",
    cook_decision,
    {
        "serve_order": "serve_order", # Preparation succeeded.
        "take_order": "take_order"    # Preparation failed.
    }
)


# ------------------------------------------------------------
# Conditional edges: serve_order -> next node
# ------------------------------------------------------------

builder.add_conditional_edges(
    "serve_order",
    serve_decision,
    {
        "end": END,                 # Serving succeeded; stop execution.
        "cook_order": "cook_order"  # Otherwise, retry preparation.
    }
)


# ============================================================
# 10. COMPILE THE GRAPH
# ============================================================

# Compile the graph into an executable workflow.
# After compilation, we can call graph.invoke() to run it.
graph = builder.compile()


# ============================================================
# 11. MAIN PROGRAM: RUN THE WORKFLOW
# ============================================================

# This block executes only when this Python file is run directly.
if __name__ == "__main__":

    # Get the initial restaurant request from the user.
    user_query = input("Enter your restaurant order request: ")

    # Start the graph with its initial shared state.
    result = graph.invoke(
        {
            "query": user_query, # Initial user request
            "order": "",         # No order has been extracted yet
            "proceed": False     # Initial decision value
        },

        # Prevent unlimited graph execution if nodes keep looping.
        config={"recursion_limit": 30}
    )

    # Display the state remaining after the graph terminates.
    print("\n--- WORKFLOW ENDED ---")
    print("Final state:", result)
