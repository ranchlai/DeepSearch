# Import necessary libraries
import re
from typing import Optional

from ds.llm.client import LLMClient
from ds.utils.search_utils import search

# --- Prompt Components ---
SEARCH_PROMPT = """# You are an search assistant that answers questions by searching and reasoning.
When you use the Search tool, carefully analyze the search results to extract relevant information.
You can search at most {max_steps} times.


## AVAILABLE TOOLS:
{tool_definitions}

## NOTES:
Each step consists of one pair of observation and action
1. **Observation**: Observe the current state (question and any previous search results), and decide your next step. For the first step, Do not conclude any search results.
2. **Action**: State the action you will take. Use EXACTLY the format `Action: ToolName[input]`. Choose only ONE action per step.
Output your Observation and Action in the following format. Please only output one observation and one action.
```
Observation: [your observation]
Action: [your action]
```

## PROGRESS
This is try {step} of {max_steps} max tries.

## ACTIONS AND OBSERVATIONS of PREVIOUS STEPS:
{history}

## CURRENT SEARCH RESULTS:
{search_results}

## USER'S QUERY:
{question}

Now begin!
"""

TOOL_DEFINITIONS = {
    "Search": {
        "description": "Use this to find information you don't have or need to verify. Formulate a specific search query.",
        "format": "Search[query]",
    },
    "Finalize": {
        "description": "Use this ONLY when you have enough information to provide a complete and accurate answer to the original question.",
        "format": "Finalize[answer]",
    },
}


class SearchAgent:
    """Search agent for answering questions using LLM reasoning and tools."""

    def __init__(self):
        self.llm_client = LLMClient(model="deepseek-reasoner")

    def build_prompt(
        self,
        question: str,
        history: str,
        step: int,
        max_steps: int,
        search_results: str = None,
    ) -> str:
        """Build the full prompt from the components."""

        # Add tool definitions
        tool_definitions = ""
        for i, (tool_name, tool_info) in enumerate(TOOL_DEFINITIONS.items(), 1):
            tool_definitions += (
                f"{i}.  **{tool_info['format']}**: {tool_info['description']}\n"
            )

        if not search_results:
            search_results = (
                "No search results yet for the first step."
                if step == 0
                else "No search results found"
            )

        history_str = ""
        for i, h in enumerate(history):
            history_str += f"Step {i+1}:\n{h}\n---\n"
        if not history_str:
            history_str = "No history yet."

        prompt = SEARCH_PROMPT.format(
            history=history_str,
            search_results=search_results,
            question=question,
            tool_definitions=tool_definitions,
            step=step + 1,
            max_steps=max_steps,
        )

        return prompt

    def parse_action(
        self, llm_response: str, step: int
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Parse the action type and input from the LLM's response.

        Args:
            llm_response: The response from the LLM
            step: The current step number (for error reporting)

        Returns:
            Tuple of (action_type, action_input) or (None, error_message) if parsing fails
        """
        action_match = re.search(
            r"Action:\s*(Search|Finalize)\[(.*?)\]",
            llm_response,
            re.DOTALL | re.IGNORECASE,
        )

        if not action_match:
            # Check if the LLM tried to give a final answer without the correct format
            if "Finalize" in llm_response.lower():
                answer_part = llm_response.split(":")[-1].strip()
                return "Finalize", answer_part

            return None, f"Agent stopped: Could not parse action after step {step + 1}."

        # Standardize action type format
        action_type = action_match.group(1).strip()
        action_type = "Search" if action_type.lower() == "search" else "Finalize"
        action_input = action_match.group(2).strip()

        return action_type, action_input

    def execute_action(
        self, action_type: str, action_input: str
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Execute the specified action and return appropriate results.

        Args:
            action_type: The type of action to execute ("Search" or "Finalize")
            action_input: The input for the action

        Returns:
            Tuple of (search_results, final_answer) where one will be None
        """
        if action_type == "Search":
            # Perform search and store results for next observation
            results = search(action_input)
            return results, None
        elif action_type == "Finalize":
            return None, action_input
        else:
            return None, f"Agent stopped due to unknown action type '{action_type}'."

    def run(self, question: str, max_steps: int = 10) -> str:
        """
        Runs the ReAct agent loop for a given question.

        Args:
            question: The user's question to answer.

        Returns:
            The final answer string, or an error/status message if it fails.
        """

        # Track the latest search results to include in the next observation context
        latest_search_results = None
        history = []
        for step in range(max_steps):
            print(f"--- Step {step + 1}/{max_steps} ---")

            # Get the base prompt structure
            current_prompt = self.build_prompt(
                question, history, step, max_steps, latest_search_results
            )
            # 1. Generate observation and Action using the LLM
            llm_response = self.llm_client.simple_query(
                current_prompt, return_reasoning=False, verbose=True
            )
            if not llm_response:
                return "Agent stopped due to LLM communication failure."

            # Append the LLM's observation process to history
            history += [f"{llm_response}\n"]

            # 2. Parse the Action from the LLM's response
            action_type, action_input = self.parse_action(llm_response, step)

            if action_type is None:
                return action_input  # Return the error message

            # 3. Execute the Action
            search_results, final_answer = self.execute_action(
                action_type, action_input
            )

            if final_answer:
                return final_answer

            latest_search_results = search_results

        # If the loop completes without a "Finalize" action
        return f"Agent stopped after {max_steps} steps without reaching a final answer."


# --- Main Execution Block ---
if __name__ == "__main__":
    # Example usage with default configuration
    agent = SearchAgent()

    # Or with custom configuration
    # custom_config = AgentConfig(model="gpt-4", max_steps=10, debug=True)
    # agent = SearchAgent(config=custom_config)

    # Example questions
    questions = [
        "What is the capital of France and what is the ReAct pattern for LLM agents?",
        "小神童3号可以在平安好车主app上购买吗？",
        "昆仑健康乐享年年终身护理保险的有效保险金额是什么意思？",
        "三国演义中，刘备的妻子是谁？",
    ]

    # Run the agent with one question
    question = questions[-1]  # Choose question index
    final_answer = agent.run(question)

    # Print the final result
    print("\n--- Agent Execution Finished ---")
    print(f"Original Question: {question}")
    print(f"Final Answer/Result: {final_answer}")
