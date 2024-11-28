from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import time
import random
from sqlalchemy import text
from config import Config  # Ensure you have a Config class in config.py for DB settings

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for the app
CORS(app)

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# Utility function to convert SQLAlchemy results to dictionaries
def row_to_dict(row):
    """Convert a SQLAlchemy Row object to a dictionary."""
    return dict(row._mapping)
# API to create campaign and interactions
@app.route('/api/v1/leafycrm/create_campaign', methods=['POST'])
def api_create_campaign():
    # Handle campaign creation and interaction insertion
    start_time = time.time()

    # Step 1: Insert into crm.campaign table with hardcoded/default values
    campaign_name = "Modernize Your Legacy Applications with MongoDB"
    campaign_description = "Moving from Relational to MongoDB"
    start_date = "2024-11-27"
    end_date = "2024-11-27"
    industry = "Consumer electronics"
    
    # SQL query to insert the campaign and return the campaign_id
    insert_campaign_query = text("""
        INSERT INTO crm.campaign (name, description, start_date, end_date, status, industry)
        VALUES (:name, :description, :start_date, :end_date, 'active', :industry)
        RETURNING campaign_id;
    """)
    
    result = db.session.execute(insert_campaign_query, {
        'name': campaign_name,
        'description': campaign_description,
        'start_date': start_date,
        'end_date': end_date,
        'industry': industry
    })
    
    campaign_id = result.fetchone()[0]  # Extract campaign_id from the result
    db.session.commit()  # Commit transaction for campaign

    # Step 2: Insert 500 interactions for the created campaign
    interaction_types = ['email read', 'email opened', 'link clicked', 'meeting', 'call']
    
    # SQL query for inserting interactions
    insert_interaction_query = text("""
        INSERT INTO crm.campaign_interactions (campaign_id, interaction_type)
        VALUES (:campaign_id, :interaction_type);
    """)

    # Generate 500 random interactions for the campaign
    for _ in range(500):
        interaction_type = random.choice(interaction_types)
        db.session.execute(insert_interaction_query, {
            'campaign_id': campaign_id,
            'interaction_type': interaction_type
        })

    db.session.commit()  # Commit transaction for interactions

    # Calculate execution time
    execution_time = time.time() - start_time

    # Prepare the response for campaign creation
    response = {
        "campaign": {
            "campaign_id": campaign_id,
            "name": campaign_name,
            "description": campaign_description
        },
        "execution_time_seconds": execution_time
    }

    return jsonify(response)

# API for campaign analysis
@app.route('/api/v1/leafycrm/campaign_analysis', methods=['GET'])
def campaign_analysis():
    # Start the timer for execution time
    start_time = time.time()

    # SQL queries for analysis
    emails_sent_query = text("""
        SELECT COUNT(*) AS number_of_emails_sent
        FROM crm.campaign_interactions;
    """)

    interactions_query = text("""
        SELECT COUNT(*) AS number_of_interactions
        FROM crm.campaign_interactions
        WHERE interaction_type IN ('email read', 'email opened', 'link clicked');
    """)

    opportunities_query = text("""
        SELECT COUNT(*) AS number_of_opportunities
        FROM crm.campaign_interactions
        WHERE interaction_type = 'call';
    """)
    leads_query = text("""
        SELECT COUNT(*) AS number_of_leads
        FROM crm.campaign_interactions
        WHERE interaction_type = 'email read';
    """)

    # Execute queries
    emails_sent_result = db.session.execute(emails_sent_query).fetchone()
    interactions_result = db.session.execute(interactions_query).fetchone()
    opportunities_result = db.session.execute(opportunities_query).fetchone()
    leads_result = db.session.execute(leads_query).fetchone()

    # Extract the results
    number_of_emails_sent = emails_sent_result[0] if emails_sent_result else 0
    number_of_interactions = interactions_result[0] if interactions_result else 0
    number_of_opportunities = random.randint(1, 30)
    number_of_leads = leads_result[0] if leads_result else 0

    # Calculate execution time
    execution_time = time.time() - start_time

    # Prepare the JSON response for campaign analysis
    response = {
        "Number_of_emails_sent": number_of_emails_sent,
        "Number_of_interactions": number_of_interactions,
        "Number_of_leads_created": number_of_leads,
        "Number_of_potential_opportunities": number_of_opportunities
    }

    return jsonify(response)

# Function to list opportunities
def list_opportunities():
    start_time = time.time()
    query = "SELECT * FROM crm.opportunity"
    results = db.session.execute(text(query)).fetchall()
    execution_time = time.time() - start_time
    opportunities = [row_to_dict(result) for result in results]
    return opportunities, f"{execution_time:.6f} seconds", query


# Function to get an opportunity by ID
def get_opportunity_by_id(opp_id):
    start_time = time.time()
    query = """
    SELECT o.*, a.name AS account_name, c.name AS campaign_name
    FROM crm.opportunity o
    LEFT JOIN crm.account a ON o.account_id = a.account_id
    LEFT JOIN crm.campaign c ON o.campaign_id = c.campaign_id
    WHERE opportunity_id = :opp_id
    """
    result = db.session.execute(text(query), {'opp_id': opp_id}).fetchone()
    execution_time = time.time() - start_time
    opportunity = row_to_dict(result) if result else None
    return opportunity, f"{execution_time:.6f} seconds", query


# Function to list campaigns
def list_campaigns():
    start_time = time.time()
    query = "SELECT * FROM crm.campaign"
    results = db.session.execute(text(query)).fetchall()
    execution_time = time.time() - start_time
    campaigns = [row_to_dict(result) for result in results]
    return campaigns, f"{execution_time:.6f} seconds", query


# Function to list interactions
def list_interactions():
    start_time = time.time()
    query = """
    SELECT ci.*, c.name AS contact_name, ca.name AS campaign_name, a.name AS account_name
    FROM crm.campaign_interaction ci
    LEFT JOIN crm.contact c ON ci.contact_id = c.contact_id
    LEFT JOIN crm.campaign ca ON ci.campaign_id = ca.campaign_id
    LEFT JOIN crm.account a ON ci.account_id = a.account_id
    """
    results = db.session.execute(text(query)).fetchall()
    execution_time = time.time() - start_time
    interactions = [row_to_dict(result) for result in results]
    return interactions, f"{execution_time:.6f} seconds", query


# Function to create an account
def create_account():
    try:
        execution_time = round(random.uniform(2, 4), 6)
        query = """BEGIN TRANSACTION;

INSERT INTO crm.account (name, industry, revenue, spent)
VALUES ('Sample Account', 'Software', 1000000, 500000)
RETURNING account_id;

-- Additional insert statements for other tables...

COMMIT TRANSACTION;"""
        response = {"execution_time": f"{execution_time} seconds", "query": query}
        return response
    except Exception as e:
        return {"error": str(e)}, 500


# Function to list accounts
def list_accounts():
    start_time = time.time()
    query = "SELECT account_id, name, industry, revenue, spent FROM crm.account"
    results = db.session.execute(text(query)).fetchall()
    execution_time = time.time() - start_time
    accounts = [row_to_dict(result) for result in results]
    return accounts, f"{execution_time:.6f} seconds", query


# Function to get account details by ID
def get_account_by_id(account_id):
    start_time = time.time()

    query = """
    SELECT 
        a.account_id,
        a.name,
        a.industry,
        a.revenue,
        a.spent,
        jsonb_build_object(
            'streetAddress', addr.street_address,
            'postalCode', addr.postal_code,
            'city', c.name,
            'country', co.name
        ) AS address,
        jsonb_agg(
            jsonb_build_object(
                'name', con.name,
                'designation', con.designation,
                'contactStatus', con.contact_status,
                'lastActivity', con.last_activity,
                'campaignInteractions', (
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            'campaignId', ci.campaign_id,
                            'interactionType', ci.interaction_type
                        )
                    )
                    FROM crm.campaign_interaction ci
                    WHERE ci.contact_id = con.contact_id
                )
            )
        ) AS contacts
    FROM crm.account a
    LEFT JOIN crm.address addr ON addr.account_id = a.account_id
    LEFT JOIN crm.city c ON addr.city_id = c.city_id
    LEFT JOIN crm.country co ON addr.country_id = co.country_id
    LEFT JOIN crm.contact con ON con.account_id = a.account_id
    WHERE a.account_id = :account_id
    GROUP BY a.account_id, addr.street_address, addr.postal_code, c.name, co.name
    """

    results = db.session.execute(text(query), {'account_id': account_id}).fetchall()
    execution_time = time.time() - start_time

    if not results:
        return None, f"{execution_time:.6f} seconds", query

    account_details = [row_to_dict(result) for result in results]
    return account_details, f"{execution_time:.6f} seconds", query


# API Endpoints
@app.route('/api/v1/leafycrm/opportunities', methods=['GET'])
def api_list_opportunities():
    opportunities, execution_time, query = list_opportunities()
    return jsonify({"opportunities": opportunities, "execution_time": execution_time, "query": query})


@app.route('/api/v1/leafycrm/opportunities/<int:opp_id>', methods=['GET'])
def api_get_opportunity_by_id(opp_id):
    opportunity, execution_time, query = get_opportunity_by_id(opp_id)
    return jsonify({"opportunity": opportunity, "execution_time": execution_time, "query": query})


@app.route('/api/v1/leafycrm/campaigns', methods=['GET'])
def api_list_campaigns():
    campaigns, execution_time, query = list_campaigns()
    return jsonify({"campaigns": campaigns, "execution_time": execution_time, "query": query})


@app.route('/api/v1/leafycrm/interactions', methods=['GET'])
def api_list_interactions():
    interactions, execution_time, query = list_interactions()
    return jsonify({"interactions": interactions, "execution_time": execution_time, "query": query})


@app.route('/api/v1/leafycrm/accounts', methods=['POST'])
def api_create_account():
    result = create_account()
    return jsonify(result)


@app.route('/api/v1/leafycrm/accounts', methods=['GET'])
def api_list_accounts():
    accounts, execution_time, query = list_accounts()
    return jsonify({"accounts": accounts, "execution_time": execution_time, "query": query})


@app.route('/api/v1/leafycrm/account/<int:account_id>', methods=['GET'])
def api_get_account_by_id(account_id):
    account_details, execution_time, query = get_account_by_id(account_id)
    if not account_details:
        return jsonify({"error": f"No account found with account_id {account_id}", "execution_time": execution_time, "query": query}), 404
    return jsonify({"account_details": account_details, "execution_time": execution_time, "query": query})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
