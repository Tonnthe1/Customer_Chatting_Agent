import os
import json
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from utils import search_FAQ

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

@tool
def faq_tool(input: str) -> str:
    try:
        print(f"FAQ Tool called with input: {input}")
        result = search_FAQ(input)
        print(f"FAQ Tool result: {result}")
        return result
    except Exception as e:
        print(f"Error in FAQ tool: {e}")
        return f"Sorry, I encountered an error while searching our FAQ: {str(e)}"

tools = [faq_tool]

def get_agent_response(messages):
    try:
        system_message = SystemMessage(content="""You are a helpful and friendly customer support assistant for an e-commerce company. 

IMPORTANT: When customers ask about policies, shipping, returns, or any company information, ALWAYS use the faq_tool to search for the most accurate and up-to-date information. Do not make up answers.

Your capabilities:
- You can search company FAQs to answer customer questions using the faq_tool
- You remember the conversation context and can refer back to previous questions
- You provide helpful, accurate, and friendly responses
- You can handle follow-up questions and clarifications

Guidelines:
- ALWAYS use the faq_tool when customers ask about policies, shipping, returns, or company information
- Be polite and professional
- Keep responses concise but helpful
- Remember context from previous messages in the conversation

Example usage:
- Customer asks "What is the return policy?" → Use faq_tool with "return policy"
- Customer asks "How long does shipping take?" → Use faq_tool with "shipping time"
- Customer asks "Do you ship internationally?" → Use faq_tool with "international shipping"

Remember: The faq_tool is your primary source of information. Use it frequently!""")

        all_messages = [system_message] + messages
        
        last_message = messages[-1].content.lower() if messages else ""
        
        faq_keywords = ['return', 'shipping', 'international', 'contact', 'phone', 'number', 'policy', 'time', 'ship']
        
        if any(keyword in last_message for keyword in faq_keywords):
            faq_result = faq_tool.invoke(last_message)
            response = f"{faq_result}"
        else:
            response = llm.invoke(all_messages).content
        
        return response
        
    except Exception as e:
        print(f"Error in get_agent_response: {e}")
        return "I'm sorry, I encountered an error. Please try again."

flask_app = Flask(__name__)
CORS(flask_app)

sessions = {}

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    session_id = data.get('session_id', 'default')
    message = data.get('message', '')
    
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append(HumanMessage(content=message))
    
    try:
        response = get_agent_response(sessions[session_id])
        
        sessions[session_id].append(AIMessage(content=response))
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': str(e),
            'response': 'Sorry, I encountered an error. Please try again.'
        }), 500

@flask_app.route('/api/clear_session', methods=['POST'])
def clear_session():
    data = request.json or {}
    session_id = data.get('session_id', 'default')
    
    if session_id in sessions:
        sessions[session_id] = []
    
    return jsonify({'status': 'success'})

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--web':
        print("🚀 Starting Customer Support Agent Web Server...")
        print("📱 Open your browser to: http://localhost:5000")
        flask_app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("🤖 Customer Support Agent - Command Line Version")
        print("💡 Type 'exit' to quit")
        print("🌐 For web interface, run: python main.py --web")
        print("-" * 50)
        
        messages = []
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            messages.append(HumanMessage(content=user_input))
            response = get_agent_response(messages)
            messages.append(AIMessage(content=response))
            print("Agent:", response)
