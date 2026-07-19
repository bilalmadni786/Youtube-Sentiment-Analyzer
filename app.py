import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from comment_import import read_comment_rows, write_comment_rows

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
chain = None

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

def get_chain():
    global chain
    if chain is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY .env file mein nahi mili.")
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=GROQ_API_KEY,
            temperature=0,
        )
        chain = prompt | llm | StrOutputParser()
    return chain


def analyze_sentiment(text: str) -> str:
    return get_chain().invoke({"text": text})


def analyze_csv_file(input_path: str, output_path: str) -> None:
    rows = read_comment_rows(input_path)
    for row in rows:
        row["sentiment_result"] = analyze_sentiment(row["text"])
    write_comment_rows(output_path, rows)


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "--csv":
        analyze_csv_file(sys.argv[2], sys.argv[3])
        print(f"CSV analysis saved to {sys.argv[3]}")
        return

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
