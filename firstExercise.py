# Create a list of 3 RTC tickets as dictionaries
tickets = [
    {
        "id": "RTC-8821",
        "severity": "High",
        "module": "PaymentService",
        "description": "Payment processing fails when using certain credit cards."
    },
    {
        "id": "RTC-8822",
        "severity": "Medium",
        "module": "UserService",
        "description": "User registration fails for some email addresses."
    },
    {
        "id": "RTC-8823",
        "severity": "High",
        "module": "InventoryService",
        "description": "Stock levels are not updating correctly."
    }
]

# Write a function called analyze_tickets(tickets)
#   that loops through the list and:
 #  - prints each ticket's id and severity
  # - counts how many are "High" severity
  # - returns the count

def analyze_tickets(tickets):
    high_severity_count = 0
    for ticket in tickets:
        print(f"Ticket ID: {ticket['id']}, Severity: {ticket['severity']}")
        if ticket["severity"] == "High":
            high_severity_count += 1
    return high_severity_count

#Call the function and print:
 #  Found X high severity tickets"
high_severity_tickets = analyze_tickets(tickets)
print(f"Found {high_severity_tickets} high severity tickets")