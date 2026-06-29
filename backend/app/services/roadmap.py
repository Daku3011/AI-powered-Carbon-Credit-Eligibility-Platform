def generate_roadmap(industry: str, metrics: dict, total_emissions: float) -> list:
    roadmap = []
    
    # Year 1 Recommendation
    if metrics.get("electricity_kwh", 0.0) > 5000.0:
        roadmap.append({
            "year": 1,
            "recommendation": "Install rooftop solar",
            "investment_inr": 500000.0,
            "savings_inr": 80000.0,
            "credits_earned": 50.0
        })
    else:
        roadmap.append({
            "year": 1,
            "recommendation": "Upgrade to energy-efficient LED lighting",
            "investment_inr": 100000.0,
            "savings_inr": 25000.0,
            "credits_earned": 15.0
        })
        
    # Year 2 Recommendation
    if industry.lower() == "manufacturing" and metrics.get("fuel_diesel_liters", 0.0) > 300.0:
        roadmap.append({
            "year": 2,
            "recommendation": "Implement waste heat recovery system",
            "investment_inr": 1200000.0,
            "savings_inr": 216000.0,
            "credits_earned": 120.0
        })
    else:
        roadmap.append({
            "year": 2,
            "recommendation": "Optimize HVAC systems and install smart thermostats",
            "investment_inr": 300000.0,
            "savings_inr": 60000.0,
            "credits_earned": 25.0
        })
        
    # Year 3 Recommendation
    if metrics.get("waste_kg", 0.0) > 100.0:
        roadmap.append({
            "year": 3,
            "recommendation": "Establish zero-waste-to-landfill recycling program",
            "investment_inr": 50000.0,
            "savings_inr": 12000.0,
            "credits_earned": 10.0
        })
    else:
        roadmap.append({
            "year": 3,
            "recommendation": "Conduct employee energy conservation training and smart power strip deployment",
            "investment_inr": 20000.0,
            "savings_inr": 5000.0,
            "credits_earned": 5.0
        })
        
    return roadmap
