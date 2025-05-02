from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Ensure the API key is provided
def create_db_from_youtube_video_url(video_url: str, openai_api_key: str) -> FAISS:
    """
    Creates a FAISS vector store from the transcript of a YouTube video.
    
    Args:
    - video_url (str): The URL of the YouTube video.
    - openai_api_key (str): The OpenAI API key.
    
    Returns:
    - FAISS: A FAISS vector store containing the video transcript.
    """
    # Initialize OpenAI embeddings with the provided API key
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    
    # Load and extract transcript from YouTube video
    loader = YoutubeLoader.from_youtube_url(video_url)
    transcript = loader.load()

    # Split the transcript into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(transcript)

    # Create a FAISS database from the documents
    db = FAISS.from_documents(docs, embeddings)
    return db


def get_response_from_query(db, query, k=4):
    """
    Retrieves a response based on a query by performing a similarity search on the video transcript.
    
    Args:
    - db (FAISS): The FAISS vector store containing video transcripts.
    - query (str): The query to search in the video transcript.
    - k (int): The number of similar documents to retrieve from the FAISS database.
    
    Returns:
    - response (str): The generated response based on the query.
    """
    # Perform similarity search on the database
    docs = db.similarity_search(query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])

    # Create a prompt template for the response generation
    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        You are a helpful assistant that can answer questions about youtube videos
        based on the video's transcript.

        Answer the following question: {question}
        By searching the following video transcript: {docs}

        Only use the factual information from the transcript to answer the question.

        If you feel like you don't have enough information to answer the question, say "I don't know".

        Your answers should be verbose and detailed.
        """
    )

    # Initialize the ChatOpenAI model
    chat_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    # Set up the LLMChain with the model and prompt template
    chain = LLMChain(llm=chat_model, prompt=prompt)

    # Run the chain to generate the response
    response = chain.run(question=query, docs=docs_page_content)
    response = response.replace("\n", "")  # Clean up the response
    
    return response, docs
