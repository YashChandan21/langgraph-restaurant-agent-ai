# 🍽️ Restaurant Ordering Agent

I built this project to learn how to use language models in a Python application where the model does more than just answer questions. I wanted to create something that could understand a food order check whether the requested quantity was available and move the food order through steps until the food order was completed or failed.

## 🛒 How It Works

The application takes a food order in language, such, as "I want 2 packets of biryani." The application extracts the dish name and quantity from the food order checks the menu and decides what should happen next.

I used LangGraph to manage the food order flow. Each step has a responsibility from confirming the food order to cooking and serving the food order. The application keeps track of the food order status and the number of retries remaining if something goes wrong.

For example if a user requests items than are available the system can handle the situation as a partial food order. If serving fails the system can retry the operation within the configured retry limit. If all attempts fail the food order ends with a failure status.

## SS 
<img width="1466" height="660" alt="image" src="https://github.com/user-attachments/assets/811ae3ed-6993-4679-acbc-6979c0d6a8cf" />

## Test
<img width="1452" height="783" alt="image" src="https://github.com/user-attachments/assets/8d242f1d-7dc0-4b9d-adea-1af3ab3ab256" />



## ⚙️ How I Built It

I used Python for the application logic and LangGraph to connect the different steps into a food order workflow.

I created a shared state to store the conversation messages food order details, current food order status and retry counters. This allows each step to access the information it needs without losing track of the food orders progress.

For understanding user messages I used a model to define the output that the LLM should give. It checks if the user is making an order accepting part of an order or asking about something that has nothing to do with ordering food.

I also added menu matching to deal with inputs that do not exactly match a menu item. This includes names and common spelling errors.

I used Groq through LangChain to run the LLM and used python-dotenv to get the API key from environment variables. I keep track of the project dependencies using uv.

## 🔄 Handling Failures

One thing I wanted to look into was what happens when a step in the process fails.

I added retry counters for order processing, cooking and serving. The workflow uses these counters to decide if another try is allowed or if it should stop.

During testing I tried a situation where the cooking step worked. The serving step kept failing. The application tried again. Again and finally returned a failure result when the retry limit was reached.

This helped me see how to manage the state through steps and how to handle failures without letting the workflow run forever.

## 📚 What I Learned

While working on this project I used LangGraph state, conditional routing, output with Pydantic and LLM integration using LangChain. I also got hands-on experience creating logic and keeping track of the state of a process through different steps.

My main lesson was that building an LLM application is more, than connecting a model to a prompt. The supporting application logic, state management and error handling are just as important.

## 🧰 Tech Stack

- 🐍 Python
- 🔀 LangGraph
- 🔗 LangChain
- ⚡ Groq
- 📋 Pydantic
- 🔐 python-dotenv
- 📦 uv

## 🚀 Running the Project

```bash
uv sync
uv run main.py
```

### 🔑 Environment Variables

Create a `.env` file in the project root and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key
```

## 👨‍💻 Author

**Yash Chandan**
