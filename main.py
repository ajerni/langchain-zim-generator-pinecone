import streamlit as st
import streamlit.components.v1 as components
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
# # only needed for initial creation of the embeddings into the vectorsrore:
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.document_loaders import TextLoader

from dotenv import load_dotenv
load_dotenv()

with st.sidebar:
    st.title('langchain-zim-generator-pinecone')
    st.markdown('''
                ## About
    This LLM-powered app creates html code based on the ZIM template from https://zimjs.com/code.html
    - Source code: [github.com/ajerni/langchain-zim-generator](https://github.com/ajerni/langchain-zim-generator-pinecone)
    ''')
    
    api_key = os.getenv("OPENAI_API_KEY")

def main():
    
    st.header("ZIM code generator")
    st.write("Use ZIM terms like circle, rectangle, ... see [ZIM Docs](https://zimjs.com/docs.html)")
    st.markdown('''
                Examples:
                - a blue rectangle centered on stage
                - 3 circles within each other. Biggest red, middle green, smallest black
                - use circles and rectangles to build something that looks like an apple
                - use an emitter to create an animation of a firework
                - etc.
                ''')
    query = st.text_input('Enter what you want the AI to build:')

    if query:
        results = generateZIMcode(query)
        st.code(results, language='html')
        components.html(results, width=512, height=384)

def generateZIMcode(query):
    
    embeddings = OpenAIEmbeddings()

    index_name = "zimdocs"

    # import pinecone
    import pinecone

    # initialize pinecone
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),  # find at app.pinecone.io
        environment=os.getenv("PINECONE_ENV"),  # next to api key in console
    )

    ## *** this part was only needed once to create the index in pinecone ***

    # loader = TextLoader("zimdocs.txt")
    # documents = loader.load()
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    # docs = text_splitter.split_documents(documents)

    # # First, check if our index already exists. If it doesn't, create it
    # if index_name not in pinecone.list_indexes():
    #     pinecone.create_index(
    #     name=index_name,
    #     metric='cosine',
    #     dimension=1536  
    # )

    # vectorstore = Pinecone.from_documents(docs, embeddings, index_name=index_name)

    ## *** end of initial creation of the vectorestore at pinecone ***

    # if the index already exists, you can load it like this:
   
    vectorstore = Pinecone.from_existing_index(index_name, embeddings)

    llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

    similars = vectorstore.similarity_search(query=query, k=3)
    qa_chain = load_qa_chain(llm=llm, chain_type="stuff")
    response = qa_chain.run(input_documents=similars, question=query)

    ZIM_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8" />
    <title>ZIM - Code Creativity</title>

    <!-- zimjs.com - JavaScript Canvas Framework -->
    <script type=module>

    import zim from "https://zimjs.org/cdn/015/zim";

    // See Docs under Frame for FIT, FILL, FULL, and TAG
    new Frame(FIT, 1024, 768, light, dark, ready);
    function ready() {
        // given F (Frame), S (Stage), W (width), H (height)
        // put code here
            
    } // end ready

    </script>
    <meta name="viewport" content="width=device-width, user-scalable=no" />
    </head>
    <body></body>
    </html>
    """

    system_template="""You are a javascript expert using the zimjs framework.
    you always use this template to embed your reply: {zim_template}. You put your reply into the template after '// put code here'. You never need to create a Stage.
    You already have the following variables given: F (Frame), S (Stage), W (width), H (height). So instead of 'stage.' use 'S.' when you code the zim content.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

    human_template="Create the follwoing in zim: {qa_result} and place it into your template (one line after the '// put code here'). Do not change the rest of your template. Reply with the whole index.html file."
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    response_chain = LLMChain(llm=llm, prompt=chat_prompt)
    res = response_chain.run(zim_template=ZIM_TEMPLATE, qa_result=response)
    print(res)
    return res

if __name__ == '__main__':
    main()
    