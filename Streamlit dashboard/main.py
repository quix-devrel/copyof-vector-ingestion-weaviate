import streamlit as st
from sentence_transformers import SentenceTransformer
import os
import pandas as pd
import weaviate
import json

os.environ["WEAVIATE_API_KEY"] = st.secrets["WEAVIATE_API_KEY"]
os.environ['collectionname'] = "BooksCatalog"
os.environ["weaviate_url"] = "https://quix-template-viv8pz43.weaviate.network"

# Initialize the sentence transformer model
encoder = SentenceTransformer('all-MiniLM-L6-v2')  # Model to create embeddings
collectionname = os.environ['collectionname']
client = ''

st.title('Simple Vector Database Search')

st.markdown('Search a Weaviate Cloud database for matches to a query (it can take a few seconds to return a result).')

# Perform the process here
try:
    print(f"Using collection name {collectionname}")

    # Initialize the QdrantClient
    # Initialize the Weaviate client. Replace the placeholder values with your actual Weaviate instance details.
    client = weaviate.Client(
        url=os.environ["weaviate_url"],
        auth_client_secret=weaviate.AuthApiKey(api_key=os.environ["WEAVIATE_API_KEY"]),
    )
    # Get the collection to search
    # qdrant.get_collection(collection_name=collectionname)

except Exception as e:
    print(f"Exception: {e}")

# Create a text input field for the search term
search_term = st.text_input("Enter your search term")
search_result = []

if search_term != "":

    try:
        # Vectorize the search term
        query_vector = encoder.encode([search_term])[0]
        
        ## Not sure how to get total entries for Weaviate, so commenting out for now
        # total_points = qdrant.get_collection(collection_name=collectionname).points_count
        total_points = 12  # hardcoded for testing
        if total_points == 0:
            st.write("Collection is empty")
        else:
            # Query the database"
            result = (
                client.query
                .get(collectionname, ["title", "description"])
                .with_near_vector({
                    "vector": query_vector,
                    "certainty": 0.7
                })
                .with_limit(2)
                .do()
            )

            # If result is a string containing JSON, parse it into a dictionary
            if isinstance(result, str):
                result = json.loads(result)

            # Now result should be a dictionary and you can access the 'data' attribute
            print(json.dumps(result, indent=4))

            # Initialize a list to hold each row of data
            resultdata = []

            # Iterate through the search results
            for res in result['data']['Get'][collectionname]:
                # Extracting data from each result
                row = {
                    'title': res['title'],
                    'description': res['description'],
                    # Uncomment and adjust the following lines if needed
                    # 'score': res['score'],
                    # 'author': res['author'],
                    # 'year': str(res['year']),
                    # 'id': res['id'],
                }
                resultdata.append(row)
                
            df = pd.DataFrame(resultdata)

            print(f"Total points stored {total_points}")
            # Display the results in a Streamlit app
            st.markdown('**Weaviate Search Results**')

            if len(resultdata) < 1:
                print("No matches")
            else:
                st.write(df)

    except Exception as e:
        print(f"Exception: {e}")
