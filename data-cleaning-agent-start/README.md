# Data Cleaning Agent

An AI-powered data cleaning agent that automatically cleans messy datasets using LangChain and LangGraph. The agent uses an LLM to generate and execute Python code for common data cleaning tasks like handling missing values, removing duplicates, and dropping low-quality columns.

## How It Works

The agent follows a simple workflow:
1. **Analyze**: Examines your dataset structure and identifies data quality issues
2. **Generate**: Uses an LLM to create custom Python cleaning code based on the data
3. **Execute**: Runs the generated code to clean your data
4. **Retry**: Automatically fixes errors if the generated code fails (up to 3 attempts)

By default the agent removes columns with more than 40% missing values, imputes missing values (mean for numeric, mode for categorical), removes duplicate rows, handles outliers, standardizes column names (lowercase, underscores), strips and lowercases text columns, and standardizes data types. The generated code may only use pandas, numpy and scikit-learn.

This approach combines the flexibility of LLMs with the reliability of pandas operations.

## Setup

### Prerequisites

- **Python 3.9 or higher** (3.9, 3.10, 3.11, 3.12, or 3.13) - **Note**: Python 3.9.7 is not supported due to a Streamlit compatibility issue
- **Poetry** (dependency manager)
- **OpenAI API Key**
- *(Optional)* **Docker** and Docker Compose, if you prefer to run the app in a container (see [Run with Docker](#run-with-docker))

### Installation Steps

1. **Install Poetry** (if not already installed):
   
   **Windows (PowerShell)**:
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
   ```
   
   **macOS/Linux**:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
   
   After installation, restart your terminal. If `poetry` command is not found:
   - **Windows**: Add `%APPDATA%\Python\Scripts` to your system PATH
   - **macOS/Linux**: Add `export PATH="$HOME/.local/bin:$PATH"` to your `~/.bashrc` or `~/.zshrc`

2. **Install dependencies**:
   ```bash
   poetry install
   ```
   
   This will install all dependencies with the exact versions specified in `poetry.lock`, ensuring consistency across all environments.

3. **Set up your OpenAI API key**:
   
   **Windows**:
   ```powershell
   copy .env.example .env
   ```
   
   **macOS/Linux**:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

### Multiple Python Versions?

If you have multiple Python versions installed and want to use a specific one:

```bash
# Tell Poetry which Python to use
poetry env use python3.11  # or python3.9, python3.10, python3.12, etc.

# Then install dependencies
poetry install
```

Poetry will create a virtual environment with your chosen Python version.

## Usage

### Streamlit Web Interface

The easiest way to use the agent is through the web interface:

```bash
poetry run streamlit run app.py
```

Then:
1. Upload your CSV file (a sample is available in `data/sample_data.csv`)
2. Click "Clean Data"
3. Review the cleaned data and the **Before vs After** comparison (rows, columns, missing values, duplicates, and a per-column summary)
4. Download the cleaned dataset as CSV
5. Optionally click **Show Generated Code** to inspect the cleaning function the LLM wrote and download it as `data_cleaner.py`
6. If something goes wrong, open the **Error Log** at the bottom of the page for details

### Run with Docker

Create your `.env` file first (see Installation step 3), then:

```bash
docker compose up --build
```

The app is available at http://localhost:8501. The API key is read from `.env` at runtime and is never baked into the image. The `logs/` folder is mounted into the container, so agent logs are saved on your machine.

### Python API

For programmatic use or integration into data pipelines:

```python
import pandas as pd
from langchain_openai import ChatOpenAI
from data_cleaning_agent import LightweightDataCleaningAgent

# Initialize the agent with an LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = LightweightDataCleaningAgent(model=llm)

# Load your messy data
df = pd.read_csv("your_data.csv")

# Run the cleaning agent
agent.invoke_agent(data_raw=df)

# Get the cleaned dataset
cleaned_df = agent.get_data_cleaned()

# Save or use the cleaned data
cleaned_df.to_csv("cleaned_data.csv", index=False)
```

**Optional: Provide custom instructions**

```python
# Give specific cleaning instructions to the agent
agent.invoke_agent(
    data_raw=df,
    user_instructions="Remove columns with more than 30% missing values and standardize date formats"
)
```

## Project Structure

```
data-cleaning-agent/
├── data_cleaning_agent/
│   ├── __init__.py
│   ├── data_cleaning_agent.py  # Main agent class
│   └── utils.py                # Utility functions
├── data/
│   └── sample_data.csv         # Sample messy dataset
├── app.py                      # Streamlit interface
├── comparison.py               # Before/after comparison UI component
├── Dockerfile                  # Container image definition
├── docker-compose.yml          # Runs the app with .env and logs/ mounted
├── .dockerignore
├── .env.example                # Template for your OpenAI API key
├── pyproject.toml              # Dependencies configuration
├── poetry.lock                 # Locked dependency versions
└── README.md
```

Generated logs are written to `logs/` (git-ignored).

**Important**: The `poetry.lock` file is committed to ensure all users get identical, tested dependency versions.
