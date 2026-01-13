
"""
Uzbekistan Tax Calculator 2025
Based on current tax legislations.
"""

def calculate_pit(income: float, is_student: bool = False) -> dict:
    """
    Calculates Personal Income Tax (PIT) for 2025.
    
    Args:
        income (float): Gross income in UZS.
        is_student (bool): If the taxpayer is a student (1% preferential rate).
        
    Returns:
        dict: Breakdown of tax and net income.
    """
    rate = 0.01 if is_student else 0.12
    # Social tax is technically separate (paid by employer usually), 
    # but for simplicity we focus on PIT withheld from employee.
    
    tax_amount = income * rate
    net_income = income - tax_amount
    
    return {
        "gross_income": income,
        "tax_rate": f"{rate * 100}%",
        "tax_amount": tax_amount,
        "net_income": net_income,
        "type": "Personal Income Tax (Student)" if is_student else "Personal Income Tax (Standard)"
    }

def calculate_cit(profit: float, category: str = "standard") -> dict:
    """
    Calculates Corporate Income Tax (CIT) for 2025.
    
    Args:
        profit (float): Taxable profit in UZS.
        category (str): 'standard', 'bank', 'mobile', 'ecommerce'.
        
    Returns:
        dict: Breakdown of tax.
    """
    rates = {
        "standard": 0.15,
        "bank": 0.20,
        "mobile": 0.20,
        "ecommerce": 0.10,
        "knitwear": 0.01  # Special preferential rate
    }
    
    rate = rates.get(category.lower(), 0.15)
    tax_amount = profit * rate
    
    return {
        "taxable_profit": profit,
        "category": category,
        "tax_rate": f"{rate * 100}%",
        "tax_amount": tax_amount,
        "net_profit": profit - tax_amount
    }

def calculate_vat(amount: float, includes_vat: bool = True) -> dict:
    """
    Calculates Value Added Tax (VAT) for 2025 (12%).
    """
    rate = 0.12
    
    if includes_vat:
        # Amount = Base * (1 + rate)  => Base = Amount / (1 + rate)
        base_amount = amount / (1 + rate)
        vat_amount = amount - base_amount
    else:
        base_amount = amount
        vat_amount = amount * rate
        amount = base_amount + vat_amount
        
    return {
        "total_amount": amount,
        "base_amount": base_amount,
        "vat_rate": "12%",
        "vat_amount": vat_amount,
        "includes_vat": includes_vat
    }
