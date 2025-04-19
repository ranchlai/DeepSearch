import os
from typing import Optional

from openai import OpenAI


class LLMClient:
    """A client for interacting with DashScope's LLM API using the OpenAI SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-reasoner",
    ):
        print(f"base_url: {base_url}, model: {model}")
        """Initialize the LLM client."""
        if "deepseek" in base_url:
            self.api_key = os.getenv("DEEPSEEK_API_KEY")
        else:
            self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "API key must be provided either through constructor or DASHSCOPE_API_KEY environment variable"
            )

        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        self.model = model

    def simple_query(
        self, prompt: str, return_reasoning: bool = False, verbose: bool = False
    ) -> tuple[str, str]:
        """
        Send a single prompt and get a response, printing streaming content.

        Args:
            prompt (str): The user's prompt

        Returns:
            tuple[str, str]: A tuple containing (reasoning_content, answer_content)
        """
        messages = [{"role": "user", "content": prompt.strip()}]
        if verbose:
            print("=" * 20)
            print(prompt.strip())
            print("=" * 20)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
        )

        reasoning_content = ""  # Complete reasoning process
        answer_content = ""  # Complete response
        is_answering = False  # Flag to track if we've moved from reasoning to answering
        if self.model == "deepseek-reasoner" and verbose:
            print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

        for chunk in response:
            if not chunk.choices:
                # Print usage if available
                if hasattr(chunk, "usage") and verbose:
                    print("\nUsage:")
                    print(chunk.usage)
            else:
                delta = chunk.choices[0].delta
                # Print and collect reasoning process
                if (
                    hasattr(delta, "reasoning_content")
                    and delta.reasoning_content is not None  # noqa
                ):
                    if verbose:
                        print(delta.reasoning_content, end="", flush=True)
                    reasoning_content += delta.reasoning_content
                else:
                    # Start response section if we haven't already
                    if delta.content and not is_answering and verbose:
                        print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                        is_answering = True
                    # Print and collect response
                    if delta.content:
                        print(delta.content, end="", flush=True)
                        answer_content += delta.content
        if verbose:
            print()  # New line after streaming completes
        if return_reasoning:
            return reasoning_content, answer_content
        else:
            return answer_content


# Example usage
if __name__ == "__main__":
    client = LLMClient(
        # base_url="https://api.deepseek.com", model="deepseek-reasoner"
        base_url="http://localhost:11434/v1",
        model="qwen2.5",
    )  # Make sure DASHSCOPE_API_KEY environment variable is set
    response = client.simple_query("9.9和9.11谁大")
    print(response)
