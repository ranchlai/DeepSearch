# DeepSearch, Minimum code to implement Deep deep using deepseek LLM (最小化代码实现deepsearch)

DeepSearch is a Python package that combines data science utilities with powerful search and LLM capabilities. It allows you to create ReAct agents that can search for information and reason through complex questions.

## Features

- **ReAct Agent**: Implements the Reasoning and Acting (ReAct) pattern for LLM agents
- **LLM Integration**: Connect to various LLM providers including DeepSeek and local models
- **Search Capabilities**: Integrated search functionality using the Serper API (Google search)

## Installation

```bash
# Clone the repository
git https://github.com/ranchlai/DeepSearch.git
cd deepsearch

# Install the package and its dependencies
pip install -e .
```

## Usage

### Basic Example

```python
from ds.search import react_agent

# Run a ReAct agent with a question
question = "小神童3号可以在平安好车主app上购买吗?"
answer = react_agent(question, max_steps=5)
print(answer)
```


## Environment Variables

The following environment variables need to be set:

- `DEEPSEEK_API_KEY`: Your DeepSeek API key
- `JINA_AI_API_KEY`: Your Jina AI API key for search, you can get it from [here](https://jina.ai/api-key)
- `SERPER_API_KEY`[Optional]: Another option is to use Serper API key for search, you can get it from [here](https://serper.dev/api-key)

## License

Apache License 2.0
