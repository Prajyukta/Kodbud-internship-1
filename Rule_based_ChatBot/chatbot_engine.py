import re
import random
from datetime import datetime

RULES = {
    "greeting": {
        "patterns": [r"\b(hi|hello|hey|howdy|hiya|good\s*(morning|afternoon|evening|day))\b"],
        "responses": [
            "Hello! 👋 How can I help you today?",
            "Hey there! What can I do for you?",
            "Hi! Great to see you. What's on your mind?",
            "Hello! I'm here and ready to help. 😊",
        ],
    },
    "farewell": {
        "patterns": [r"\b(bye|goodbye|see\s*you|take\s*care|cya|later|quit|exit)\b"],
        "responses": [
            "Goodbye! Have a wonderful day! 👋",
            "See you later! Take care! 😊",
            "Bye! Feel free to come back anytime.",
            "Farewell! It was nice chatting with you! 🌟",
        ],
    },
    "thanks": {
        "patterns": [r"\b(thanks|thank\s*you|thx|ty|appreciated|cheers)\b"],
        "responses": [
            "You're welcome! 😊",
            "Happy to help! Anything else?",
            "No problem at all!",
            "Anytime! That's what I'm here for. 🤖",
        ],
    },
    "name": {
        "patterns": [r"\b(your\s*name|who\s*are\s*you|what\s*are\s*you|introduce\s*yourself)\b"],
        "responses": [
            "I'm RuleBot 🤖 — a friendly rule-based chatbot built with Python & Flask!",
            "My name is RuleBot! I respond based on predefined rules.",
            "I'm RuleBot, your helpful Python chatbot. Nice to meet you!",
        ],
    },
    "how_are_you": {
        "patterns": [r"\b(how\s*are\s*you|how\s*do\s*you\s*do|how\s*r\s*u|you\s*okay|how\s*are\s*things)\b"],
        "responses": [
            "I'm doing great, thanks for asking! How about you? 😄",
            "Running perfectly! All systems operational. 🤖",
            "Fantastic! I'm always in a good mood. How are you?",
        ],
    },
    "time":    {"patterns": [r"\b(time|current\s*time|what\s*time|clock)\b"],   "responses": ["__TIME__"]},
    "date":    {"patterns": [r"\b(date|today|what\s*day|current\s*date|day\s*today)\b"], "responses": ["__DATE__"]},
    "weather": {
        "patterns": [r"\b(weather|temperature|forecast|rain|sunny|cloudy)\b"],
        "responses": ["I can't fetch live weather, but you can check weather.com! ☀️🌧️"],
    },
    "help": {
        "patterns": [r"\b(help|assist|support|what\s*can\s*you\s*do|capabilities|features)\b"],
        "responses": [(
            "Here's what I can help with:\n"
            "• 👋 Greetings & farewells\n"
            "• 🤖 About me\n"
            "• 🕐 Current time & date\n"
            "• 😄 Jokes\n"
            "• 🧮 Basic math (e.g. 12 * 8)\n"
            "• 💬 Small talk & FAQs\n"
            "• 🌤️ Weather info\n"
            "• 📞 Contact & support"
        )],
    },
    "joke": {
        "patterns": [r"\b(joke|funny|make\s*me\s*laugh|humor|tell\s*me\s*a\s*joke)\b"],
        "responses": [
            "Why don't scientists trust atoms? Because they make up everything! 😂",
            "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads. 🍫",
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
            "What do you call a fish without eyes? A fsh! 🐟",
            "Why did the developer go broke? He used up all his cache! 💸",
            "How many programmers to change a light bulb? None — it's a hardware problem! 💡",
        ],
    },
    "math": {
        "patterns": [r"(\d+\.?\d*)\s*[\+\-\*\/\^%]\s*(\d+\.?\d*)"],
        "responses": ["__MATH__"],
    },
    "age": {
        "patterns": [r"\b(how\s*old\s*are\s*you|your\s*age|when\s*were\s*you\s*born)\b"],
        "responses": ["I was born the moment someone ran `python app.py`. Very young! 🐣"],
    },
    "creator": {
        "patterns": [r"\b(who\s*(made|created|built|programmed)\s*you|your\s*(creator|developer))\b"],
        "responses": ["I was created by a Python developer using Flask & rule-based logic! 🐍"],
    },
    "language": {
        "patterns": [r"\b(what\s*(language|programming|coded|written)\s*(are\s*you|in)|built\s*with)\b"],
        "responses": ["I'm built with Python 🐍 + Flask for the web interface! Pure rule-based logic, no ML."],
    },
    "python": {
        "patterns": [r"\b(python|programming|coding|developer|flask)\b"],
        "responses": [
            "Python + Flask is a powerful combo! 🐍🌶️ Perfect for web chatbots.",
            "Flask makes serving chatbots so easy. Love it! ✨",
        ],
    },
    "affirmation": {
        "patterns": [r"\b(yes|yeah|yep|sure|absolutely|of\s*course|ok|okay|alright)\b"],
        "responses": ["Great! What else can I help you with? 😊", "Awesome! Feel free to ask me anything."],
    },
    "negation": {
        "patterns": [r"\b(no|nope|nah|not\s*really|never\s*mind|nothing)\b"],
        "responses": ["No worries! Let me know if you change your mind. 😊"],
    },
    "love": {
        "patterns": [r"\b(love|like\s*you|i\s*love|you're\s*(great|awesome|cool|amazing))\b"],
        "responses": ["Aw, that's sweet! 🤖❤️", "You're making me blush — if robots could blush! 😊"],
    },
    "insult": {
        "patterns": [r"\b(stupid|dumb|useless|terrible|hate\s*you|worst|awful)\b"],
        "responses": ["I'm sorry to hear that. I'll try to do better! 😔"],
    },
    "faq_hours": {
        "patterns": [r"\b(open|hours|operating|available|when\s*are\s*you)\b"],
        "responses": ["I'm available 24/7 — I never sleep! 🌙⚡"],
    },
    "faq_contact": {
        "patterns": [r"\b(contact|email|phone|reach|support|customer)\b"],
        "responses": ["For support, please email support@example.com 📧"],
    },
    "faq_price": {
        "patterns": [r"\b(price|cost|fee|charge|subscription|free|paid|premium)\b"],
        "responses": ["I'm completely free to use! Open-source Python 💚"],
    },
}

FALLBACK = [
    "Hmm, I'm not sure about that. Try asking something else! 🤔",
    "I didn't quite catch that. Could you rephrase? 💬",
    "That's beyond my current knowledge. Ask me something simple! 🙂",
    "Interesting! I don't have an answer for that yet. Try 'help'.",
]


class RuleBasedChatbot:
    def __init__(self, name="RuleBot"):
        self.name = name

    def respond(self, user_input: str) -> str:
        text = user_input.strip().lower()
        if not text:
            return "Please type something! I'm listening. 👂"

        math_result = self._try_math(text)
        if math_result:
            return math_result

        for _, rule in RULES.items():
            for pattern in rule["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    response = random.choice(rule["responses"])
                    return self._resolve(response, text)

        return random.choice(FALLBACK)

    def _resolve(self, response, user_input):
        now = datetime.now()
        if response == "__TIME__":
            return f"The current time is {now.strftime('%I:%M %p')} ⏰"
        if response == "__DATE__":
            return f"Today is {now.strftime('%A, %B %d, %Y')} 📅"
        if response == "__MATH__":
            return self._try_math(user_input) or "I couldn't compute that."
        return response

    def _try_math(self, text):
        match = re.search(r"(\d+\.?\d*)\s*([\+\-\*\/\^%])\s*(\d+\.?\d*)", text)
        if not match:
            return None
        a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
        try:
            if op == "+":   result = a + b
            elif op == "-": result = a - b
            elif op == "*": result = a * b
            elif op == "/":
                if b == 0: return "Oops! Can't divide by zero. 🚫"
                result = a / b
            elif op == "^": result = a ** b
            elif op == "%": result = a % b
            else: return None
            r = int(result) if result == int(result) else round(result, 6)
            return f"🧮 {match.group(1)} {op} {match.group(3)} = **{r}**"
        except Exception:
            return None
