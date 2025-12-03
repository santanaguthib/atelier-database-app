"""
Automated testing script for all user roles in Atelier application
Tests all 10 modules with each user role
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AtelierApp'))

from colorama import Fore, Style, init
from AtelierApp.database import DatabaseConnection

# Don't import modules individually - they have interactive menus

init(autoreset=True)

# Test users
USERS = [
    {"username": "atelier_admin", "password": "Admin@2025!Strong", "role": "admin", "name": "ADMIN"},
    {"username": "manager", "password": "Manager@2025!Pass", "role": "manager", "name": "MANAGER"},
    {"username": "tailor_user", "password": "Tailor@2025!Pass", "role": "tailor", "name": "TAILOR"},
    {"username": "cashier", "password": "Cashier@2025!Pass", "role": "cashier", "name": "CASHIER"}
]

# Module test queries - simple checks without interactive menus
MODULES = [
    {"name": "Audit", "query": "SELECT name FROM sys.server_audit_specifications WHERE is_state_enabled = 1"},
    {"name": "DDM", "query": "SELECT TOP 1 CustomerID, CustomerName, Phone, Address FROM Customers"},
    {"name": "Extended Events", "query": "SELECT name FROM sys.dm_xe_sessions WHERE name LIKE 'Atelier%'"},
    {"name": "Backup", "query": "SELECT name FROM msdb.dbo.sysjobs WHERE name LIKE 'Atelier%Backup%'"},
    {"name": "TDE", "query": "SELECT d.name, dek.encryption_state FROM sys.dm_database_encryption_keys dek JOIN sys.databases d ON dek.database_id = d.database_id WHERE d.name = 'Atelier'"},
    {"name": "Filegroups", "query": "SELECT name, type_desc FROM sys.filegroups"},
    {"name": "Triggers", "query": "SELECT name, is_disabled FROM sys.triggers WHERE parent_class = 0"},
    {"name": "Procedures", "query": "SELECT name FROM sys.procedures WHERE name LIKE 'sp_%'"},
    {"name": "Views", "query": "SELECT name FROM sys.views"},
    {"name": "Functions", "query": "SELECT name FROM sys.objects WHERE type IN ('FN', 'TF', 'IF')"}
]

def test_connection(user):
    """Test if user can connect to database"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"Testing {user['name']} ({user['username']})")
    print(f"{'='*80}{Style.RESET_ALL}")
    
    db = DatabaseConnection(user['username'], user['password'], user['role'])
    if db.connect():
        print(f"{Fore.GREEN}✓ Connection successful{Style.RESET_ALL}")
        
        # Test basic query
        query = "SELECT SYSTEM_USER AS CurrentUser, USER_NAME() AS DatabaseUser, @@VERSION AS SQLVersion"
        columns, results = db.execute_query(query)
        if results:
            print(f"\n{Fore.GREEN}Current User: {results[0][0]}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Database User: {results[0][1]}{Style.RESET_ALL}")
        
        db.disconnect()
        return True
    else:
        print(f"{Fore.RED}✗ Connection failed{Style.RESET_ALL}")
        return False

def test_module_access(user, module):
    """Test if user can access specific module functionality"""
    db = DatabaseConnection(user['username'], user['password'], user['role'])
    if not db.connect():
        return False, "Connection failed"
    
    try:
        columns, results = db.execute_query(module['query'])
        db.disconnect()
        
        if columns is not None:
            return True, len(results) if results else 0
        return False, "Query returned None"
        
    except Exception as e:
        db.disconnect()
        return False, str(e)

def main():
    """Main testing function"""
    print(f"\n{Fore.YELLOW}{'='*80}")
    print(f"ATELIER APPLICATION - COMPREHENSIVE USER TESTING")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    results = []
    
    # Test each user
    for user in USERS:
        # Test connection
        connection_ok = test_connection(user)
        
        if connection_ok:
            # Test each module
            module_results = []
            print(f"\n{Fore.CYAN}Testing module access for {user['name']}:{Style.RESET_ALL}")
            
            for module in MODULES:
                success, info = test_module_access(user, module)
                status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if success else f"{Fore.RED}✗{Style.RESET_ALL}"
                info_str = f"({info} items)" if isinstance(info, int) else f"Error: {info}"
                print(f"  {status} {module['name']}: {info_str}")
                module_results.append({
                    "module": module['name'],
                    "success": success,
                    "info": info
                })
            
            results.append({
                "user": user['name'],
                "connection": True,
                "modules": module_results
            })
        else:
            results.append({
                "user": user['name'],
                "connection": False,
                "modules": []
            })
    
    # Print summary
    print(f"\n{Fore.YELLOW}{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    for result in results:
        conn_status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if result['connection'] else f"{Fore.RED}✗{Style.RESET_ALL}"
        print(f"{conn_status} {result['user']}: ", end="")
        
        if result['connection']:
            successful_modules = sum(1 for m in result['modules'] if m['success'])
            total_modules = len(result['modules'])
            print(f"{successful_modules}/{total_modules} modules accessible")
            
            # Show failed modules if any
            failed = [m['module'] for m in result['modules'] if not m['success']]
            if failed:
                print(f"  {Fore.YELLOW}Failed: {', '.join(failed)}{Style.RESET_ALL}")
        else:
            print("Connection failed")
    
    print(f"\n{Fore.GREEN}Testing completed!{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
