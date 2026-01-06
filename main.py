from intent_parse import intent_parse, item_parse, summarize
from search import product_search, compare_search
import pandas as pd
from datetime import datetime
import numpy as np

import faiss
from sentence_transformers import SentenceTransformer

cart = pd.DataFrame(columns=['Name', 'Link', 'Added On'])
vector_db = faiss.IndexFlatL2(384)

vectordb_model = SentenceTransformer('all-MiniLM-L6-v2')

while True:
    query = input(">> ")

    # Intent Parse
    intent, conversation = intent_parse(query, existing_conversation=None)
    
    # Action
    # 1. Product Search 
    if intent['intent'] in ['product_search', 'recommendation', 'purchase']:

        if intent['category'] in (None, 'None'):
            items, conversation = item_parse(query)
            intent['category'] = items['items']


        result = product_search(intent)

        if result:
            print(f"Here are the Top Results from Google Shopping Regarding yout Request:\n")
            summary_query = f""

            for r in result:
                for x in ['title', 'price', 'rating', 'reviews', 'source']:
                    if x in r:
                        summary_query = summary_query + f"{x.upper()}: {r[x]}"

                    summary_query = summary_query + f"\n"
                
            summary, _ = summarize(summary_query)
            print(summary)

    # 2. Compare Products 
    elif intent['intent'] == 'compare':

        if intent['items_for_comparison'] is not None:
            result = compare_search(intent['items_for_comparison'])
            summary_query = f""

            for r in result:
                for x in ['title', 'price', 'rating', 'reviews', 'source']:
                    if x in r:
                        summary_query = summary_query + f"{x.upper()}: {r[x]}"
                    
                    summary_query = summary_query + f"\n"
                
            summary, _ = summarize(summary_query)
            print(summary)

    # 3. Shopping Cart 
    elif intent['intent'] == 'cart_action':

        items, _ = item_parse(query)
        items['items'] = items['items'] or intent['items_for_comparison']
        #print("ITEMS: ", items['items'])

        if intent['cart_action'] == 'add':
            if items['items'] in (None, "None"):
                print("No Items Found")

            else:
                for i in items['items']:
                    print(f"looking for {i}...")
                    result = product_search(i)
                    if result:
                        row = {'Name':result[0]['title'], 
                               'Link': result[0]['product_link'], 
                               'Added On': datetime.now()}
                        
                        cart = pd.concat([cart, pd.DataFrame([row])], ignore_index=True)
                        word_embeddings = vectordb_model.encode([result[0]['title']]).astype('float32')
                        vector_db.add(word_embeddings)
                        print(f"Added {result[0]['title']} to Shopping Cart")

        elif intent['cart_action'] == 'remove':
            
            items, _ = item_parse(query)
            items['items'] = items['items'] or intent['items_for_comparison']

            if items['items'] in (None, "None"): # Rework
                print("No Items Found")

            else: # Rework
                if type(items['items']) == str:
                    items['items'] = [items['items']]

                for i in items['items']:
                    query_text = [i]
                    query_embedding = vectordb_model.encode(query_text).astype('float32')
                    distances, indices = vector_db.search(query_embedding, k=1)

                    print(f"Removed {cart['Name'][indices[0][0]]} from Shopping Cart")
                    cart = cart.drop(indices[0][0]).reset_index(drop=True)
                    vector_db.remove_ids(faiss.IDSelectorArray(indices[0]))
                    

        elif intent['cart_action'] == 'empty':
            cart = pd.DataFrame(columns=['Name', 'Link', 'Added On'])
            vector_db = faiss.IndexFlatL2(384)

        elif intent['cart_action'] == 'show':
            print(cart)

    # 4. Dont Know
    elif intent['intent'] == 'jibberish':
        print("Shut Up")

    else:
        print("I dont know what you're talking about")

    print()
        

    