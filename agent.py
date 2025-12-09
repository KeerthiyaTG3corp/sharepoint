import requests
import json
import subprocess
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')


MCP_URL = "http://127.0.0.1:5005"

def ask_llm(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3:8b"],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.stdout.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        return f"ERROR calling LLM: {e}"


def call_mcp(action):
    """
    Calls your MCP server based on the LLM's selected action.
    """
    if action == "scan":
        r = requests.post(f"{MCP_URL}/scan")
        return r.json()

    elif action == "summary":
        r = requests.get(f"{MCP_URL}/summary")
        return r.json()

    elif action == "metadata":
        r = requests.get(f"{MCP_URL}/metadata")
        return r.json()

    elif action == "logs":
        r = requests.get(f"{MCP_URL}/logs")
        return r.json()
    
    elif action == "send_email":
        print("🔄 Running fresh scan before sending email...")
        requests.post(f"{MCP_URL}/scan")
    
        print("📄 Fetching updated summary...")
        summary = requests.get(f"{MCP_URL}/summary").json().get("summary")
    
        print("✉ Sending email report...")
        result = requests.post(f"{MCP_URL}/send_report", json={"summary": summary}).json()
    
        print("MCP Result:", result)
        return result

    else:
        return {"error": "Unknown action"}


def run_agent():
    print("Local SharePoint Agent Ready!")
    print("Type commands like:")
    print("- scan sharepoint")
    print("- show summary")
    print("- show metadata")
    print("- get logs")
    print("- send email")
    print("- exit")
    print("------------------------------------------------------")

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        # 🔥 Ask local LLM for the action
        llm_prompt = f"""
        You are an AI agent controlling a SharePoint MCP server.
        Convert user instructions into a JSON action.
        
        Allowed actions:
        - scan : triggers SharePoint scan
        - summary : get SharePoint summary
        - metadata : fetch stored metadata
        - logs : fetch log entries
        - send_email : send summary report to Outlook user
        
        User message: "{user_input}"
        
        Respond ONLY in JSON. Example:
        {{"action": "scan"}}
        """

        llm_response = ask_llm(llm_prompt)

        print("\nLLM Response:", llm_response)

        try:
            action = json.loads(llm_response).get("action")
        except:
            print("❌ LLM did not return valid JSON. Response was:")
            print(llm_response)
            continue

        result = call_mcp(action)

        print("\nMCP Result:", json.dumps(result, indent=2))


if __name__ == "__main__":
    run_agent()
