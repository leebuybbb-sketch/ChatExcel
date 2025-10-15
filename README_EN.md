# ChatExcel

## Project Introduction

ChatExcel is a tool dedicated to intelligent spreadsheet data analysis, designed to help users unlock the value of Excel data in a convenient and efficient manner. Built on the **deepseek large language model** for its core analytical capabilities, this tool can deeply understand the structure and logic of Excel data, supporting multi-dimensional analysis and mining of various types of spreadsheet data.

Compared with traditional Excel analysis tools, ChatExcel eliminates the need for users to master complex functions or coding knowledge. Users only need to perform simple operations to trigger the intelligent analysis process. The analysis results can be presented in two forms: **structured tables** or **visual charts** (such as line charts, bar charts, pie charts, etc.). This not only meets the need for accurate data viewing but also facilitates intuitive insight into data trends and correlations. It is suitable for various scenarios, including daily office data summarization, business report analysis, and student assignment data processing.

## Functional Case Demonstrations

The following are screenshots of ChatExcel in actual use, intuitively showing the tool's operation interface and the effect of analysis results:

### Case 1: Data Import and Basic Analysis Interface

![ChatExcel Data Import and Basic Analysis Interface](img/1.png)

### Case 2: Analysis Results in Table Form

![ChatExcel Analysis Results in Table Form](img/2.png)

### Case 3: Analysis Results in Visual Chart Form

![ChatExcel Analysis Results in Visual Chart Form](img/3.png)

## Requirements

1. **Python Version**: Python 3.10 or above is required (Python 3.10/3.11 is recommended for better compatibility).

2. **Dependency Installation**: Install all required dependency packages for the project using the following command to ensure the tool runs properly:

```
pip install -r requirements.txt
```

*Note: If dependency conflicts occur during installation, you can try creating a virtual environment (e.g., using venv or conda) before reinstalling to avoid affecting other local project environments.*

## Run

Follow the steps below to quickly launch the ChatExcel application:

1. Open the terminal (Command Prompt or PowerShell for Windows; Terminal for Mac/Linux).

2. Navigate to the project root directory (use the `cd project-path` command to switch, e.g., `cd ~/ChatExcel`).

3. Execute the following command in the terminal:

```
streamlit run main\_app.py
```

4. After the command is executed successfully, the terminal will output the access link for the application (usually including a local link `http://localhost:8501` and a local area network link).

5. The system will automatically open this link in the default browser. If it does not open automatically, you can manually copy the link and paste it into the browser's address bar to access the ChatExcel operation interface.

