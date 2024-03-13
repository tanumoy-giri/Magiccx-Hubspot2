import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# HubSpot API key
api_key = os.getenv('HUBSPOT_API_KEY')

# Define Flask app
app = Flask(__name__)
CORS(app)

# Function to fetch ticket ID associated with a meeting ID
def get_ticket_id(meeting_id):
    endpoint = f'https://api.hubapi.com/crm/v3/objects/meetings/{meeting_id}?associations=ticket'
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        data = response.json()
        ticket_id = data.get("associations", {}).get("tickets", {}).get("results", [{}])[0].get("id")
        return ticket_id
    else:
        print(f"Failed to fetch ticket ID: {response.text}")
        return None

# Function to update ticket properties
def update_ticket_properties(ticket_id, summarize, record_link, meeting_id, full_conversation_link, sentiment_analysis):
    endpoint = f'https://api.hubapi.com/crm/v3/objects/tickets/{ticket_id}'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    payload = {
        "properties": {
            "magiccx_meeting_summarize": summarize,
            "meeting_record_link": record_link,
            "magiccx_meeting_id": meeting_id,
            "magiccx_full_conversation_link": full_conversation_link,
            "magiccx_sentiment_analysis": sentiment_analysis
        }
    }
    response = requests.patch(endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        return {"message": "Ticket properties updated successfully."}
    else:
        return {"error": f"Failed to update ticket properties: {response.text}"}

# API route to handle ticket update request
@app.route('/update-ticket', methods=['POST'])
def update_ticket_route():
    data = request.json
    meeting_id = data.get('meetingId')
    summarize = data.get('summarize')
    record_link = data.get('recordLink')
    full_conversation_link = data.get('fullConversationLink')
    sentiment_analysis = data.get('sentimentAnalysis')
    
    if not meeting_id:
        return jsonify({"error": "Meeting ID is required."}), 400
    
    ticket_id = get_ticket_id(meeting_id)
    if ticket_id:
        result = update_ticket_properties(ticket_id, summarize, record_link, meeting_id, full_conversation_link, sentiment_analysis)
        return jsonify(result), 200
    else:
        return jsonify({"error": "Failed to update ticket properties."}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
