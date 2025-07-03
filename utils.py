import json
import os

def load_faq(filepath: str):
    try:
        # Get the absolute path to the data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, filepath)
        
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading FAQ file: {e}")
        return []

def search_FAQ(user_input: str) -> str:
    try:
        faq_list = load_faq("data/faq.json")
        
        if not faq_list:
            return "Sorry, I couldn't access our FAQ database at the moment."
        
        keyword_mapping = {
            'return': ['return', 'refund', 'policy', 'return policy'],
            'shipping': ['shipping', 'delivery', 'ship', 'time', 'how long'],
            'international': ['international', 'china', 'canada', 'uk', 'australia', 'europe'],
            'contact': ['contact', 'phone', 'number', 'call', 'support'],
            'track': ['track', 'tracking', 'order', 'where'],
            'free': ['free', 'cost', 'price', 'shipping cost']
        }
        
        user_input_lower = user_input.lower().strip()
        
        for category, keywords in keyword_mapping.items():
            if any(keyword in user_input_lower for keyword in keywords):
                for faq in faq_list:
                    question_lower = faq["question"].lower()
                    if any(keyword in question_lower for keyword in keywords):
                        return faq["answer"]
        
        for faq in faq_list:
            question_words = faq["question"].lower().split()
            input_words = user_input_lower.split()
            
            common_words = set(question_words) & set(input_words)
            if len(common_words) >= 1:
                return faq["answer"]
        
        return "I couldn't find a specific answer to your question in our FAQ. Please try rephrasing your question or contact our support team for assistance."
        
    except Exception as e:
        print(f"Error in search_FAQ: {e}")
        return f"Sorry, I encountered an error while searching our FAQ: {str(e)}"
