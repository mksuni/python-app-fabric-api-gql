from flask import Flask, request, jsonify
from azure.identity import ClientSecretCredential
import requests
import json
from flask import Flask, jsonify, render_template
import os

app = Flask(__name__)

# Azure Service Principal credentials
TENANT_ID = os.environ["TENANTID"]
CLIENT_ID = os.environ["CLIENTID"]
CLIENT_SECRET = os.environ["CLIENTSECRET"]
FABRIC_API_SCOPE = "https://analysis.windows.net/powerbi/api/.default"
FABRIC_GRAPHQL_ENDPOINT = os.environ["FABRIC_GRAPHQL_ENDPOINT"]

# Authenticate using the Service Principal
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)


variables= {}

@app.route("/")
def index():
   return render_template('index.html')


@app.route("/api/gql", methods=["POST"])
def run_graphql_query():
    """Send a GraphQL query to the Microsoft Fabric API."""
    try:
        # Get an access token
        token = credential.get_token(FABRIC_API_SCOPE)
        access_token = token.token

        # Get the GraphQL query from the request
        # Define a static GraphQL query
        query = """        
         query{
            customers(first: 5) {
               items {
                  CustomerID
                  FirstName
                  LastName
                  EmailAddress         
               }
            }
            vProductAndDescriptions {
               items {
                  ProductID
                  Name
                  Description
                  ProductModel       
               }
            }
            vGetAllCategories {
               items {
                  ProductCategoryID
                  ParentProductCategoryName
                  ProductCategoryName
               }
            }
         }
      """

  
        # Send the GraphQL query to the Fabric API
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            FABRIC_GRAPHQL_ENDPOINT,
            json={'query': query, 'variables': variables},
            headers=headers
        )

        # Return the response from the Fabric API
        return response.json(), response.status_code

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True)