# services.py
import os
from dotenv import load_dotenv
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from models import ArticleContent, TwitterThread

load_dotenv()

class ContentRepurposer:
    def __init__(self):
        from pydantic import SecretStr

        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key is None:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        _google_api_key = SecretStr(google_api_key)
        # Initialize Gemini model and embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
        )
        self.llm = ChatGoogleGenerativeAI(
            # model="gemini-1.5-flash",
            model="gemini-2.0-flash-exp",
            temperature=0.7)
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def process_pdf(self, pdf_path: str) -> ArticleContent:
        """Process local PDF and create embeddings"""
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        
        # Extract text
        text = " ".join(page.page_content for page in pages)
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create and store embeddings in Chroma
        self.vectordb = Chroma.from_texts(
            texts=chunks,
            embedding=self.embeddings,
            persist_directory="./data/chroma_db"
        )
        
        # Extract title and author
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        title = lines[0] if lines else "Untitled"
        author = lines[1] if len(lines) > 1 else None
        
        return ArticleContent(
            title=title,
            content=text,
            author=author,
            url=pdf_path
        )
    
    def get_relevant_chunks(self, query: str, k: int = 3) -> List[str]:
        """Retrieve relevant chunks from vector database"""
        results = self.vectordb.similarity_search(query, k=k)
        return [doc.page_content for doc in results]
    
    def generate_twitter_thread(self, article: ArticleContent) -> TwitterThread:
        """Generate Twitter thread using Gemini"""
        # First, get the most relevant chunks for different aspects
        intro_chunks = self.get_relevant_chunks("introduction and main points")
        technical_chunks = self.get_relevant_chunks("technical details and implementation")
        conclusion_chunks = self.get_relevant_chunks("conclusion and key takeaways")
        
        # thread_prompt = PromptTemplate(
        #     input_variables=["title", "intro", "technical", "conclusion"],
        #     template="""
        #     Create an engaging Twitter thread (8-10 tweets) about this technical article.
            
        #     Title: {title}
            
        #     Introduction Context:
        #     {intro}
            
        #     Technical Details:
        #     {technical}
            
        #     Key Takeaways:
        #     {conclusion}
            
        #     Rules:
        #     1. First tweet should be attention-grabbing
        #     2. Each tweet must be under 280 characters
        #     3. Use clear numbering (1/n format)
        #     4. Include relevant technical details
        #     5. End with a call to action
        #     6. Make it educational and informative
            
        #     Format the output as a list of tweets, one per line.
        #     After the tweets, suggest 3-5 relevant hashtags on new lines starting with #.
        #     """
        # )

        thread_prompt = PromptTemplate(
            input_variables=["title", "intro", "technical", "conclusion"],
            template="""
            Write an engaging Twitter thread (8-10 tweets) summarizing this technical article in an approachable and human-like style.

            Title: {title}

            Introduction Context:
            {intro}

            Technical Details:
            {technical}

            Key Takeaways:
            {conclusion}

            Guidelines:
            1. Start with a hook that grabs attention (e.g., a surprising fact, bold statement, or thought-provoking question).
            2. Use a conversational tone and explain complex details simply, without jargon.
            3. Include concise tweets under 280 characters, following the 1/n numbering format.
            4. Break down the key insights logically, and make each tweet build curiosity for the next one.
            5. Include relevant examples, analogies, or comparisons to aid understanding.
            6. End the thread with a strong conclusion and a call to action (e.g., "Read the full article," "Follow for more insights").
            7. Make it relatable, educational, and engaging.

            Output format:
            - A numbered list of tweets, with each tweet on a new line.
            - After the tweets, suggest 3-5 hashtags that summarize the thread, starting with #.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=thread_prompt)
        result = chain.run({
            "title": article.title,
            "intro": "\n".join(intro_chunks),
            "technical": "\n".join(technical_chunks),
            "conclusion": "\n".join(conclusion_chunks)
        })
        
        # Parse the result into tweets and hashtags
        lines = result.split("\n")
        tweets = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
        hashtags = [tag.strip() for tag in lines if tag.strip().startswith("#")]
        
        # Ensure we have at least one tweet and hashtag
        if not tweets:
            tweets = ["Thread about " + article.title]
        if not hashtags:
            hashtags = ["#AI", "#TechNews"]
            
        return TwitterThread(tweets=tweets, hashtags=hashtags)
    
    def process_article(self, pdf_path: str) -> TwitterThread:
        """Main method to process article and generate content"""
        try:
            article = self.process_pdf(pdf_path)
            thread = self.generate_twitter_thread(article)
            return thread
        except Exception as e:
            print(f"Error processing article: {str(e)}")
            raise