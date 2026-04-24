import pandas as pd
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from datetime import datetime
import os

# ====================== USE GROQ (Free & Fast) ======================
os.environ["OPENAI_API_KEY"] = "gsk_..............."          # ← Paste your Groq key here
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"   # or "mixtral-8x7b-32768"

# Rest of your code remains exactly the same...
# ====================== MOCK ORACLE SCM DATA ======================
data = {
    'item_id': ['ITEM001', 'ITEM002', 'ITEM003', 'ITEM004', 'ITEM005'],
    'item_name': ['Laptop Dell XPS', 'Mouse Logitech', 'HP Printer', 'Office Chair', 'Samsung Monitor'],
    'current_stock': [12, 45, 8, 25, 5],
    'reorder_point': [15, 30, 10, 20, 8],
    'monthly_demand': [25, 60, 18, 12, 15],
    'lead_time_days': [7, 3, 10, 5, 8],
    'unit_cost': [45000, 800, 12000, 6500, 18000]
}

inventory_df = pd.DataFrame(data)

# ====================== TOOLS ======================
@tool
def get_inventory_details(item_id: str) -> str:
    """Get current inventory details from Oracle SCM (mock)"""
    item = inventory_df[inventory_df['item_id'] == item_id.upper()]
    if item.empty:
        return "Item not found!"
    return item.to_string(index=False)

@tool
def calculate_reorder_quantity(item_id: str) -> str:
    """Calculate suggested reorder quantity using standard formula"""
    item = inventory_df[inventory_df['item_id'] == item_id.upper()]
    if item.empty:
        return "Item not found!"
    
    row = item.iloc[0]
    reorder_point = row['reorder_point']
    current_stock = row['current_stock']
    monthly_demand = row['monthly_demand']
    lead_time = row['lead_time_days']
    
    # Simple EOQ + Safety stock logic
    daily_demand = monthly_demand / 30
    lead_time_demand = daily_demand * lead_time
    suggested_qty = max(0, int(lead_time_demand + reorder_point - current_stock + 10))
    
    return f"""
Item: {row['item_name']}
Current Stock: {current_stock}
Reorder Point: {reorder_point}
Suggested Reorder Qty: {suggested_qty}
Estimated Cost: ₹{suggested_qty * row['unit_cost']:,}
    """

@tool
def create_replenishment_request(item_id: str, quantity: int, reason: str) -> str:
    """Simulate creating Requisition / Move Order in Oracle SCM"""
    return f"""
✅ REPLENISHMENT REQUEST CREATED SUCCESSFULLY!

Item ID     : {item_id}
Quantity    : {quantity}
Type        : Purchase Requisition + Move Order
Reason      : {reason}
Date        : {datetime.now().strftime('%Y-%m-%d %H:%M')}
Status      : Approved & Sent to Procurement
    """

# ====================== AGENTS ======================
inventory_analyst = Agent(
    role='Senior Inventory Analyst',
    goal='Analyze stock levels and decide if replenishment is needed with proper quantity',
    backstory='You are an expert Oracle SCM Functional Analyst with 10+ years experience in Inventory module.',
    tools=[get_inventory_details, calculate_reorder_quantity],
    verbose=True
)

replenishment_specialist = Agent(
    role='Replenishment Specialist',
    goal='Create accurate replenishment requests in Oracle SCM format',
    backstory='You handle execution of inventory replenishment in Oracle Fusion SCM.',
    tools=[create_replenishment_request],
    verbose=True
)

# ====================== TASKS ======================
task1 = Task(
    description="""Analyze the following item and decide whether replenishment is needed.
    Item ID: {item_id}
    Give clear reasoning with current stock vs reorder point.""",
    expected_output="Detailed analysis with recommendation (Replenish / Do Not Replenish) and suggested quantity",
    agent=inventory_analyst
)

task2 = Task(
    description="""If replenishment is recommended, create the official replenishment request.
    Use proper quantity from previous analysis.""",
    expected_output="Confirmation that replenishment request was created in Oracle SCM format",
    agent=replenishment_specialist
)

# ====================== CREW ======================
crew = Crew(
    agents=[inventory_analyst, replenishment_specialist],
    tasks=[task1, task2],
    process=Process.sequential,
    verbose=True
)

# ====================== RUN ======================
if __name__ == "__main__":
    print("🚀 Oracle SCM Inventory Replenishment Agent Started!\n")
    
    item_id = input("Enter Item ID (e.g., ITEM001): ").strip().upper()
    
    result = crew.kickoff(inputs={'item_id': item_id})
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(result)