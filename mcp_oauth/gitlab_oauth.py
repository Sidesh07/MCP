from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
import requests
import logging

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(
    filename="mcp_server.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Starting MCP server for GitLab OAuth.")

# Initialize MCP server
mcp = FastMCP("gitlab_oauth")

# GitLab OAuth credentials from environment variables
GITLAB_CLIENT_ID = os.getenv("GITLAB_CLIENT_ID")
GITLAB_CLIENT_SECRET = os.getenv("GITLAB_CLIENT_SECRET")
GITLAB_REDIRECT_URI = os.getenv("GITLAB_REDIRECT_URI")

# GitLab OAuth endpoints
AUTHORIZE_URL = "https://gitlab.com/oauth/authorize"
TOKEN_URL = "https://gitlab.com/oauth/token"

@mcp.tool()
def get_authorization_url(state: str) -> str:
    """
    Generate the GitLab OAuth authorization URL.
    """
    try:
        logging.info("Generating authorization URL.")
        params = {
            "client_id": GITLAB_CLIENT_ID,
            "redirect_uri": GITLAB_REDIRECT_URI,
            "response_type": "code",
            "state": state,
            "scope": "read_user"
        }
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        url = f"{AUTHORIZE_URL}?{query_string}"
        logging.info(f"Authorization URL generated: {url}")
        return url
    except Exception as e:
        logging.error(f"Error generating authorization URL: {e}")
        return str(e)

@mcp.tool()
def exchange_code_for_token(code: str) -> dict:
    """
    Exchange the authorization code for an access token.
    """
    try:
        logging.info("Exchanging authorization code for access token.")
        payload = {
            "client_id": GITLAB_CLIENT_ID,
            "client_secret": GITLAB_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": GITLAB_REDIRECT_URI
        }
        response = requests.post(TOKEN_URL, data=payload)
        response.raise_for_status()
        token_data = response.json()
        logging.info(f"Access token retrieved successfully: {token_data}")
        return token_data
    except requests.RequestException as e:
        logging.error(f"Error exchanging code for token: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    try:
        logging.info("Running MCP server...")
        mcp.run(transport="stdio")
    except Exception as e:
        logging.error(f"Error running MCP server: {e}")
