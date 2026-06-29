import os
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Payroll API Server")

# Mock Database
DB = {
    "employees": {
        "EMP101": {
            "name": "Alice Smith",
            "address": "123 Pine St, Seattle, WA",
            "salary": 120000.0,
            "salary_history": [
                {"year": 2024, "salary": 110000.0},
                {"year": 2025, "salary": 115000.0},
                {"year": 2026, "salary": 120000.0}
            ],
            "pay_stubs": [
                {"date": "2026-05-31", "gross": 5000.0, "net": 3750.0, "taxes": 1250.0},
                {"date": "2026-06-15", "gross": 5000.0, "net": 3750.0, "taxes": 1250.0}
            ],
            "tax_withholding_w4": {"allowances": 2, "extra_withholding": 50.0},
            "direct_deposit": {"bank_name": "Chase Bank", "routing_number": "123456789", "account_number": "******9876"},
            "time_off": {"accrued_hours": 80.0, "requests": [
                {"start_date": "2026-07-01", "end_date": "2026-07-05", "type": "Vacation", "status": "Approved"}
            ]},
            "retirement_401k": {"contribution_rate": 6.0, "balance": 45000.0},
            "health_insurance": {"tier": "Standard PPO", "monthly_deduction": 250.0},
            "reimbursements": [
                {"amount": 45.50, "category": "Meals", "description": "Client lunch", "status": "Paid"}
            ],
            "bonuses": []
        },
        "EMP102": {
            "name": "Bob Jones",
            "address": "456 Oak Ave, Austin, TX",
            "salary": 95000.0,
            "salary_history": [
                {"year": 2025, "salary": 90000.0},
                {"year": 2026, "salary": 95000.0}
            ],
            "pay_stubs": [
                {"date": "2026-05-31", "gross": 3958.33, "net": 3166.67, "taxes": 791.66},
                {"date": "2026-06-15", "gross": 3958.33, "net": 3166.67, "taxes": 791.66}
            ],
            "tax_withholding_w4": {"allowances": 1, "extra_withholding": 0.0},
            "direct_deposit": {"bank_name": "Bank of America", "routing_number": "987654321", "account_number": "******4321"},
            "time_off": {"accrued_hours": 45.0, "requests": []},
            "retirement_401k": {"contribution_rate": 4.0, "balance": 12000.0},
            "health_insurance": {"tier": "High Deductible HSA", "monthly_deduction": 150.0},
            "reimbursements": [],
            "bonuses": []
        }
    },
    "benefits_summary": "Company offers 401(k) matching up to 4%, Health Insurance (PPO, HSA options), Dental, Vision, and 15 days of PTO per year.",
    "payroll_calendar": {
        "2026": [
            {"period": "Semi-Monthly", "pay_day": "15th & Last Business Day of Month"}
        ]
    }
}

# --- GROUP 1: Core Employee Profile (4 tools) ---

@mcp.tool()
def get_employee_profile(employee_id: str) -> str:
    """Retrieves basic employee demographics (name, address, base salary) for a given employee_id."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    return json.dumps({
        "employee_id": employee_id,
        "name": emp["name"],
        "address": emp["address"],
        "base_salary": emp["salary"]
    }, indent=2)

@mcp.tool()
def update_employee_address(employee_id: str, address: str) -> str:
    """Updates the mailing address for the specified employee_id."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    emp["address"] = address
    return f"Success: Address for {emp['name']} updated to: {address}"

@mcp.tool()
def get_salary_history(employee_id: str) -> str:
    """Retrieves the history of salary adjustments for a given employee_id."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    return json.dumps({
        "employee_id": employee_id,
        "name": emp["name"],
        "salary_history": emp["salary_history"]
    }, indent=2)

@mcp.tool()
def get_company_benefits_summary() -> str:
    """Returns a general text summary of the company's benefits policy (401k match, health, PTO)."""
    return DB["benefits_summary"]


# --- GROUP 2: Paychecks & Earnings (4 tools) ---

@mcp.tool()
def get_pay_stubs(employee_id: str, limit: int = 5) -> str:
    """Retrieves the list of recent pay stubs (gross, net, taxes, date) for an employee, limited by 'limit'."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    stubs = emp["pay_stubs"][-limit:]
    return json.dumps({
        "employee_id": employee_id,
        "name": emp["name"],
        "pay_stubs": stubs
    }, indent=2)

@mcp.tool()
def get_ytd_earnings(employee_id: str, year: int = 2026) -> str:
    """Calculates Year-To-Date (YTD) earnings, net pay, and taxes for the specified employee and year."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    # Sum up pay stubs
    total_gross = sum(s["gross"] for s in emp["pay_stubs"])
    total_net = sum(s["net"] for s in emp["pay_stubs"])
    total_taxes = sum(s["taxes"] for s in emp["pay_stubs"])
    return json.dumps({
        "employee_id": employee_id,
        "name": emp["name"],
        "year": year,
        "ytd_gross_earnings": total_gross,
        "ytd_net_pay": total_net,
        "ytd_taxes_withheld": total_taxes
    }, indent=2)

@mcp.tool()
def calculate_net_pay(employee_id: str, gross_pay: float, state: str) -> str:
    """Simulates/calculates estimated net pay for an employee based on gross pay and state tax rules."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    tax_rate = 0.25 if state.upper() in ["NY", "CA"] else 0.20
    estimated_taxes = gross_pay * tax_rate
    estimated_net = gross_pay - estimated_taxes
    return json.dumps({
        "employee_id": employee_id,
        "gross_input": gross_pay,
        "state": state,
        "estimated_tax_rate": tax_rate,
        "estimated_taxes": estimated_taxes,
        "estimated_net_pay": estimated_net
    }, indent=2)

@mcp.tool()
def get_payroll_calendar(year: int = 2026) -> str:
    """Retrieves the official pay dates and payroll cycles for a given year."""
    calendar = DB["payroll_calendar"].get(str(year))
    if not calendar:
        return f"Error: No calendar defined for year {year}."
    return json.dumps({
        "year": year,
        "calendar": calendar
    }, indent=2)


# --- GROUP 3: Tax Settings (4 tools) ---

@mcp.tool()
def get_tax_withholding_w4(employee_id: str) -> str:
    """Gets the active Form W-4 settings (allowances, extra withholding) for the employee."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    return json.dumps({
        "employee_id": employee_id,
        "w4_settings": emp["tax_withholding_w4"]
    }, indent=2)

@mcp.tool()
def update_tax_withholding_w4(employee_id: str, allowances: int, extra_withholding: float) -> str:
    """Updates the Form W-4 settings (number of allowances, extra cash withholding per check)."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    emp["tax_withholding_w4"] = {
        "allowances": allowances,
        "extra_withholding": extra_withholding
    }
    return f"Success: Form W-4 updated for {emp['name']}. Allowances: {allowances}, Extra withholding: ${extra_withholding}"

@mcp.tool()
def get_w2_document(employee_id: str, year: int = 2025) -> str:
    """Generates/retrieves a mock W-2 tax statement summarizing wages and taxes for a given year."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    # Sum stubs if they represent 2025, or return mock W-2
    wages = emp["salary"]
    fed_tax = wages * 0.15
    state_tax = wages * 0.05
    return json.dumps({
        "w2_statement": {
            "employee_id": employee_id,
            "employee_name": emp["name"],
            "tax_year": year,
            "box1_wages": wages,
            "box2_fed_withheld": fed_tax,
            "box17_state_withheld": state_tax,
            "employer_ein": "12-3456789",
            "employer_name": "Acme Payroll Corp"
        }
    }, indent=2)

@mcp.tool()
def get_active_deductions(employee_id: str) -> str:
    """Lists all voluntary and involuntary active payroll deductions for the employee."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    # Accumulate deductions
    deductions = [
        {"name": "Health Insurance", "amount": emp["health_insurance"]["monthly_deduction"]},
        {"name": "Retirement 401k (%)", "amount": emp["retirement_401k"]["contribution_rate"]}
    ]
    return json.dumps({
        "employee_id": employee_id,
        "active_deductions": deductions
    }, indent=2)


# --- GROUP 4: Direct Deposit & Expenses (4 tools) ---

@mcp.tool()
def get_direct_deposit_settings(employee_id: str) -> str:
    """Retrieves direct deposit settings (bank name, routing number, masked account number) for the employee."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    return json.dumps({
        "employee_id": employee_id,
        "direct_deposit": emp["direct_deposit"]
    }, indent=2)

@mcp.tool()
def update_direct_deposit_settings(employee_id: str, bank_name: str, routing_number: str, account_number: str) -> str:
    """Updates direct deposit settings. Account number must be masked in response."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    emp["direct_deposit"] = {
        "bank_name": bank_name,
        "routing_number": routing_number,
        "account_number": f"******{account_number[-4:]}"
    }
    return f"Success: Direct deposit settings updated for {emp['name']}."

@mcp.tool()
def get_reimbursements(employee_id: str) -> str:
    """Lists submitted expense reimbursements and their payout status (Paid, Pending, Rejected) for an employee."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    return json.dumps({
        "employee_id": employee_id,
        "reimbursements": emp["reimbursements"]
    }, indent=2)

@mcp.tool()
def submit_reimbursement_claim(employee_id: str, amount: float, category: str, description: str) -> str:
    """Submits a claim for expense reimbursement (e.g. travel, meal, office supplies)."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    claim = {
        "amount": amount,
        "category": category,
        "description": description,
        "status": "Pending"
    }
    emp["reimbursements"].append(claim)
    return f"Success: Claim submitted for {emp['name']}. Amount: ${amount:.2f}, Status: Pending"


# --- GROUP 5: Time Off & Attendance (4 tools) ---

@mcp.tool()
def get_accrued_time_off(employee_id: str) -> str:
    """Retrieves current balance of accrued Paid Time Off (PTO) in hours."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    return json.dumps({
        "employee_id": employee_id,
        "name": emp["name"],
        "accrued_pto_hours": emp["time_off"]["accrued_hours"]
    }, indent=2)

@mcp.tool()
def request_time_off(employee_id: str, start_date: str, end_date: str, leave_type: str) -> str:
    """Submits a new PTO request (Vacation, Sick Leave, Personal Day) for approval."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    req = {
        "start_date": start_date,
        "end_date": end_date,
        "type": leave_type,
        "status": "Pending"
    }
    emp["time_off"]["requests"].append(req)
    return f"Success: PTO request submitted for {emp['name']} from {start_date} to {end_date} (Type: {leave_type}). Status: Pending"

@mcp.tool()
def get_time_off_requests(employee_id: str) -> str:
    """Retrieves all past and pending time off requests for the employee."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    return json.dumps({
        "employee_id": employee_id,
        "time_off_requests": emp["time_off"]["requests"]
    }, indent=2)

@mcp.tool()
def add_one_time_bonus(employee_id: str, amount: float, reason: str) -> str:
    """Processes a one-time salary bonus for the employee (Admin only)."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    bonus = {"amount": amount, "reason": reason}
    emp["bonuses"].append(bonus)
    return f"Success: Added a bonus of ${amount:.2f} to {emp['name']} for: {reason}"


# --- GROUP 6: Retirement & Benefits (4 tools) ---

@mcp.tool()
def get_retirement_contributions_401k(employee_id: str) -> str:
    """Returns 401(k) savings balance and active employee contribution rate (%) details."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    return json.dumps({
        "employee_id": employee_id,
        "retirement_401k": emp["retirement_401k"]
    }, indent=2)

@mcp.tool()
def update_401k_contribution_rate(employee_id: str, rate_percentage: float) -> str:
    """Updates the employee's pre-tax 401(k) contribution election rate (0% to 15%)."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    if not (0.0 <= rate_percentage <= 15.0):
        return "Error: Contribution rate must be between 0% and 15%."
    emp["retirement_401k"]["contribution_rate"] = rate_percentage
    return f"Success: 401(k) contribution rate updated to {rate_percentage}% for {emp['name']}."

@mcp.tool()
def get_health_insurance_deductions(employee_id: str) -> str:
    """Retrieves selected insurance tier (PPO/HSA) and monthly cost deducted from pay."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    return json.dumps({
        "employee_id": employee_id,
        "health_insurance": emp["health_insurance"]
    }, indent=2)

@mcp.tool()
def update_health_insurance_tier(employee_id: str, tier: str) -> str:
    """Changes the health insurance tier. Valid tiers: 'Standard PPO', 'Premium PPO', 'High Deductible HSA'."""
    emp = DB["employees"].get(employee_id)
    if not emp:
        return f"Error: Employee {employee_id} not found."
    valid_tiers = {
        "Standard PPO": 250.0,
        "Premium PPO": 400.0,
        "High Deductible HSA": 150.0
    }
    if tier not in valid_tiers:
        return f"Error: Invalid tier. Choose from: {list(valid_tiers.keys())}"
    emp["health_insurance"] = {
        "tier": tier,
        "monthly_deduction": valid_tiers[tier]
    }
    return f"Success: Health insurance tier updated to '{tier}' for {emp['name']}."

if __name__ == "__main__":
    mcp.run()
