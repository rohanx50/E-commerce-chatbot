import sqlite3
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import re

from app.sql import comprehension_prompt

load_dotenv()


def run_query(query):
    if query.strip().upper().startswith('SELECT'):
        with sqlite3.connect('/Users/rohandesu/ecom/app/db.sqlite') as conn:
            df = pd.read_sql_query(query, conn)
            return df



def generate_sql_query(query):
    sql_prompt = """You are an expert in understanding the database schema and generating SQL queries for a natural language question asked pertaining to the data you have. The schema is provided in the schema tags.

    <SCHEMA>
    table: product

    fields:
    - product_link: string (hyperlink to product)
    - title: string (name of the product)
    - brand: string (brand of the product)
    - price: integer (price of the product in Indian Rupees)
    - discount: float (discount on the product. 10 percent discount is represented as 0.1, 20 percent as 0.2, and such.)
    - avg_rating: float (average rating out of 5. Range 0–5, 5 is the highest.)
    - total_ratings: integer (number of ratings for the product)
    </SCHEMA>

    Make sure whenever you try to search for the brand name, the name can be in any case.
    Also make sure to use `LIKE` instead of `=` in condition. Never use `= 'LIKE'`, use only `LIKE`.
    The query should strictly use only the fields in SELECT clause (i.e., SELECT *)

    Output SQL query as needed, nothing more. Always provide the SQL in between the <SQL> </SQL> tags.
    """

    client = Groq()
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": sql_prompt,
            },
            {
                "role": "user",
                "content": query,
            }
        ],
        temperature=0.2,
        max_tokens=1024
    )

    return completion.choices[0].message.content


def sql_chain(question):
    sql_query=generate_sql_query(question)
    pattern ="<SQL>(.*?)</SQL>"
    matches=re.findall(pattern, sql_query,re.DOTALL)
    if len(matches)==0:
        return "could nit find sql query"
    print(matches[0].strip())

    response=run_query(matches[0].strip())

    if response is None:
        return "could not find the data regarding the query"

    context=response.to_dict(orient='records')
    answer=data_comprehension(question,context)
    return answer



comprehension_prompt = """You are an expert in understanding the context of the question and replying based on the data pertaining to the question provided. You will be provided with Question: and Data:. The data will be in the form of an array or a dataframe or dict. Reply based on only the data provided as Data for answering the question asked as Question. Do not write anything like 'Based on the data' or any other technical words. Just a plain simple natural language response.
The Data would always be in context to the question asked. For example is the question is “What is the average rating?” and data is “4.3”, then answer should be “The average rating for the product is 4.3”. So make sure the response is curated with the question and data. Make sure to note the column names to have some context, if needed, for your response.
There can also be cases where you are given an entire dataframe in the Data: field. Always remember that the data field contains the answer of the question asked. All you need to do is to always reply in the following format when asked about a product: 
Produt title, price in indian rupees, discount, and rating, and then product link. Take care that all the products are listed in list format, one line after the other. Not as a paragraph.
For example:
1. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
2. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
3. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>

"""


def data_comprehension(question,context):

    client = Groq()
    llm = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{'role': 'system', 'content': comprehension_prompt},
                  {'role': 'user', 'content':f"QUESTION:{question},DATA:{context}" }
                  ]

    )

    return llm.choices[0].message.content



















if __name__=='__main__':
    ans=sql_chain(" nike shoes in price range of 5000 to 10000")
    print(ans)


