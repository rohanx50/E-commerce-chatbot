import uuid

import pandas as pd
import chromadb
from sqlalchemy.testing.suite.test_reflection import metadata
from groq import Groq
from dotenv import load_dotenv
load_dotenv()




faqs_path='/Users/rohandesu/ecom/app/resources/faq_data.csv'
chroma_client=chromadb.Client()
collection_name_faq='faqs'







def ingest_faq_data(path):
    if collection_name_faq not in [c.name for c in chroma_client.list_collections()]:
        print('Ingesting faq data')
        collection = chroma_client.get_or_create_collection(
            name=collection_name_faq
        )
        df = pd.read_csv(path)
        document = df['question'].to_list()
        metadata= [{'answer': ans} for ans in df['answer'].to_list()]
        id= [f"id_{i}" for i in range(df.shape[0])]

        collection.add(
            documents=document,
            metadatas=metadata,
            ids=id)
        print('Ingested faq data')
    else:
        print('collection alresdy exists')

def get_relevant_qa(query):
    collection=chroma_client.get_collection(name=collection_name_faq)
    result=collection.query(
        query_texts=[query],
        n_results=2
    )
    return result

def faq_chain(query):
    result=get_relevant_qa(query)
    context = ' '.join([r.get('answer') for r in result['metadatas'][0]])

    answer= generate_answers(query, context)
    return answer





def generate_answers(query,context):
    prompt = f'''
    Given the question and context below, generate answer based on the context only.
    if u don't find the answer inside the content the say "i don't know"
    . do not make things up.

    QUESTION: {query}
    CONTEXT:  {context}

    '''
    client = Groq()
    llm = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{'role': 'user', 'content': prompt}]

    )

    return llm.choices[0].message.content











if __name__ == '__main__':
    ingest_faq_data(faqs_path)
    query = "what's your policy on defective products"
    answer = faq_chain(query)
    print(answer)
