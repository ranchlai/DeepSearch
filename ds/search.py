# Import necessary libraries
import re

from ds.llm.client import LLMClient
from ds.utils.search_utils import search

REACT_PROMPT = """You are an AI assistant that answers questions by reasoning step-by-step and using tools when needed.

AVAILABLE TOOLS:
1.  **Search[query]**: Use this to find information you don't have or need to verify. Formulate a specific search query.
2.  **Final Answer[answer]**: Use this ONLY when you have enough information to provide a complete and accurate answer to the original question.

PROCESS:
Follow this cycle strictly:
1.  **Thought**: Analyze the current state (question, previous observations). Decide your next step: either search for more info or provide the final answer. Explain your reasoning briefly.
2.  **Action**: State the action you will take. Use EXACTLY the format `Action: ToolName[input]`. Choose only ONE action per step.
3.  **Observation**: The result of your action (e.g., search results) will be provided by the system. You will use this in your next Thought.

EXAMPLE:
Question: What is the main programming language used for Android development?
Thought: The user is asking about the primary language for Android apps. I should search to confirm the current standard language.
Action: Search[main programming language for Android development]
Observation: Search results indicate Kotlin is now the preferred language for Android development, although Java is also widely used.
Thought: The search confirms Kotlin is preferred, but Java is also relevant. I can now formulate the final answer including both.
Action: Final Answer[Kotlin is the preferred programming language for Android development, recommended by Google. Java is also widely used, especially for older codebases.]

BEGIN!
"""

llm_client = LLMClient(model="deepseek-reasoner")


# --- ReAct Agent Logic ---
def react_agent(question: str, max_steps: int = 5):
    """
    Runs the ReAct agent loop for a given question.

    Args:
        question: The user's question to answer.
        max_steps: Maximum number of Thought-Action-Observation cycles allowed.

    Returns:
        The final answer string, or an error/status message if it fails.
    """
    # Get the base prompt structure
    base_prompt = REACT_PROMPT

    # Initialize the 'scratchpad' or history for the current reasoning chain
    history = f"Question: {question}\n"
    print("--- Starting ReAct Agent ---")
    print(f"Initial Question: {question}\n")

    for step in range(max_steps):
        print(f"--- Step {step + 1}/{max_steps} ---")

        # Prepare the prompt for the LLM by combining the base instructions and current history
        current_prompt = (
            base_prompt + history + "Thought:"
        )  # Prompt the LLM to start with a thought
        # print(f"Sending Prompt to LLM:\n{current_prompt}\n") # Uncomment for deep debugging

        # 1. Generate Thought and Action using the LLM
        llm_response = llm_client.simple_query(current_prompt)
        # print(f"LLM Raw Response:\n{llm_response}\n") # Uncomment for deep debugging

        if not llm_response:
            print("Agent Error: Failed to get response from LLM. Stopping.")
            return "Agent stopped due to LLM communication failure."

        # Append the LLM's thought process (which should precede the action) to history
        # The LLM is prompted for "Thought:", so its response starts there.
        history += f"Thought: {llm_response}\n"
        print(f"Thought: {llm_response}")  # Display the thought process

        # 2. Parse the Action from the LLM's response
        # Use regex to find "Action: ToolName[Input]" pattern. Handles multi-line inputs within brackets.
        action_match = re.search(
            r"Action:\s*(Search|Final Answer)\[(.*?)\]",
            llm_response,
            re.DOTALL | re.IGNORECASE,
        )

        if not action_match:
            # If no valid action is found, the agent might be stuck or the LLM deviated.
            print(
                "Agent Warning: Could not parse a valid action from the LLM response."
            )
            # Check if the LLM tried to give a final answer without the correct format
            if "final answer" in llm_response.lower():
                answer_part = llm_response.split(":")[-1].strip()  # Simple heuristic
                print(
                    f"Attempting to extract final answer heuristically: {answer_part}"
                )
                return answer_part
            history += "Observation: Failed to parse action. Stopping.\n"
            return f"Agent stopped: Could not parse action after step {step + 1}. Review LLM response and prompt. History:\n{history}"

        # Fix the capitalization issue by standardizing action type format
        action_type = action_match.group(1).strip().lower()
        action_input = action_match.group(2).strip()

        # Standardize action type names for comparison
        if action_type.lower() == "search":
            action_type = "Search"
        elif action_type.lower() == "final answer":
            action_type = "Final Answer"

        history += f"Action: {action_type}[{action_input}]\n"  # Log the successfully parsed action
        print(f"Action: {action_type}[{action_input}]")

        # 3. Execute the Action and Get Observation
        if action_type == "Search":
            # Call the (dummy or real) search API
            observation = search(action_input)
            history += f"Observation: {observation}\n"
            print(f"Observation: {observation}")
        elif action_type == "Final Answer":
            # Agent has decided it has the answer
            print("\n--- Final Answer Determined ---")
            return action_input  # Return the final answer
        else:
            # This case should ideally not be reached if the regex and action types are correct
            print(f"Agent Error: Unknown action type '{action_type}'. Stopping.")
            return f"Agent stopped due to unknown action type '{action_type}' after step {step + 1}."

        # Optional: Check for excessive history length if token limits are a concern
        # if len(current_prompt) > 3500: # Example token budget check
        #     print("Warning: Prompt approaching token limits, may need truncation strategy.")

    # If the loop completes without a "Final Answer" action
    print("\nAgent Warning: Maximum steps reached without providing a final answer.")
    return f"Agent stopped after {max_steps} steps. The question might be too complex, require more steps, or the agent got stuck. Final history:\n{history}"


# --- Main Execution Block ---
if __name__ == "__main__":

    # question = "What is the capital of France and what is the ReAct pattern for LLM agents?"
    question = "小神童3号可以在平安好车主app上购买吗？"

    # Run the agent
    final_answer = react_agent(question, max_steps=5)

    # Print the final result
    print("\n--- Agent Execution Finished ---")
    print(f"Original Question: {question}")
    print(f"Final Answer/Result: {final_answer}")
