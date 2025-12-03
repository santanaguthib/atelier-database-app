"""
Detailed DDM (Dynamic Data Masking) test for all users
Tests to verify masking works correctly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AtelierApp'))

from colorama import Fore, Style, init
from database import DatabaseConnection
from tabulate import tabulate

init(autoreset=True)

# Test users
USERS = [
    {"username": "atelier_admin", "password": "Admin@2025!Strong", "role": "admin", "name": "ADMIN", "should_see_unmasked": True},
    {"username": "manager", "password": "Manager@2025!Pass", "role": "manager", "name": "MANAGER", "should_see_unmasked": True},
    {"username": "tailor_user", "password": "Tailor@2025!Pass", "role": "tailor", "name": "TAILOR", "should_see_unmasked": False},
    {"username": "cashier", "password": "Cashier@2025!Pass", "role": "cashier", "name": "CASHIER", "should_see_unmasked": False}
]

def test_ddm_for_user(user):
    """Test DDM masking for a user"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"Testing DDM for {user['name']} ({user['username']})")
    print(f"Expected: {'UNMASKED data' if user['should_see_unmasked'] else 'MASKED data'}")
    print(f"{'='*80}{Style.RESET_ALL}")
    
    db = DatabaseConnection(user['username'], user['password'], user['role'])
    if not db.connect():
        print(f"{Fore.RED}✗ Connection failed{Style.RESET_ALL}")
        return
    
    query = """
    SELECT TOP 5
        CustomerID,
        CustomerName,
        Phone,
        Address
    FROM Customers
    ORDER BY CustomerID
    """
    
    columns, results = db.execute_query(query)
    db.disconnect()
    
    if columns and results:
        print(f"\n{Fore.GREEN}Query successful - {len(results)} rows returned{Style.RESET_ALL}")
        table = tabulate(results, headers=columns, tablefmt='grid')
        print(table)
        
        # Check if data is masked
        first_phone = str(results[0][2]) if len(results) > 0 and len(results[0]) > 2 else ""
        is_masked = 'X' in first_phone or first_phone == ""
        
        if user['should_see_unmasked']:
            if is_masked:
                print(f"\n{Fore.RED}⚠ WARNING: Data appears MASKED but should be UNMASKED{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}✓ Correct: Data is UNMASKED{Style.RESET_ALL}")
        else:
            if is_masked:
                print(f"\n{Fore.GREEN}✓ Correct: Data is MASKED{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}⚠ WARNING: Data appears UNMASKED but should be MASKED{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Query failed{Style.RESET_ALL}")

def main():
    """Main testing function"""
    print(f"\n{Fore.YELLOW}{'='*80}")
    print(f"DYNAMIC DATA MASKING (DDM) - DETAILED TEST")
    print(f"{'='*80}{Style.RESET_ALL}")
    
    for user in USERS:
        test_ddm_for_user(user)
    
    print(f"\n{Fore.GREEN}{'='*80}")
    print(f"DDM Testing completed!")
    print(f"{'='*80}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
