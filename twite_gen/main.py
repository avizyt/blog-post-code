import os
from dotenv import load_dotenv
from services import ContentRepurposer


def main():
    # Load environment variables
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not found")

    # Initialize repurposer
    repurposer = ContentRepurposer()

    # Path to your local PDF
    # pdf_path = "data/guide_to_jax.pdf"
    pdf_path = "data/build_llm_powered_app.pdf"

    try:
        thread = repurposer.process_article(pdf_path)

        print("Generated Twitter Thread:")
        for i, tweet in enumerate(thread.tweets, 1):
            print(f"\nTweet {i}/{len(thread.tweets)}:")
            print(tweet)

        print("\nSuggested Hashtags:")
        print(" ".join(thread.hashtags))

    except Exception as e:
        print(f"Failed to process article: {str(e)}")


if __name__ == "__main__":
    main()
