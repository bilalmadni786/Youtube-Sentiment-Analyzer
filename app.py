import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY .env file mein nahi mili.")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """Tum ek Urdu text sentiment analyzer ho.
Diye gaye Urdu text ka sentiment analyze karo aur SIRF yeh format mein jawab do:

Sentiment: [Positive / Negative / Neutral]
Wajah: [1-2 line mein wajah Urdu ya Roman Urdu mein]

Koi extra text mat likho.""",
    ),
    ("human", "{text}"),
])

chain = prompt | llm | StrOutputParser()


def analyze_sentiment(text: str) -> str:
    return chain.invoke({"text": text})


def main():
    print("=" * 50)
    print("   Urdu Sentiment Analyzer (Groq + LangChain)")
    print("=" * 50)
    print("Bahar nikalne ke liye 'exit' ya 'quit' type karo\n")

    while True:
        user_input = input("Urdu text darj karo: ").strip()

        if not user_input:
            print("Koi text nahi diya. Dobara koshish karo.\n")
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Khuda Hafiz!")
            break

        print("\nAnalyze ho raha hai...\n")
        result = analyze_sentiment(user_input)
        print(result)
        print("-" * 50 + "\n")


if __name__ == "__main__":
    main()
