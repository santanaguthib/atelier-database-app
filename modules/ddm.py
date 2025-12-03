"""
Dynamic Data Masking (DDM) Module - Compare data visibility between roles
"""
from database import DatabaseConnection
from colorama import Fore, Style


def show_ddm_menu(db):
    """Display DDM menu for testing data masking"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}")
        print("DYNAMIC DATA MASKING - Role-Based Data Protection")
        print(f"{'='*80}{Style.RESET_ALL}")
        print("1. View Masked Columns Configuration")
        print("2. Compare Data as ADMIN (Unmasked)")
        print("3. Compare Data as CASHIER (Masked)")
        print("4. Side-by-Side Comparison")
        print("5. Test DDM with All Roles")
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
        
        if choice == '1':
            view_masked_columns_config(db)
        elif choice == '2':
            view_data_as_admin()
        elif choice == '3':
            view_data_as_cashier()
        elif choice == '4':
            side_by_side_comparison()
        elif choice == '5':
            test_all_roles()
        elif choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_masked_columns_config(db):
    """View DDM configuration for all tables"""
    query = """
    SELECT 
        OBJECT_NAME(c.object_id) AS TableName,
        c.name AS ColumnName,
        t.name AS DataType,
        c.max_length AS MaxLength,
        CASE WHEN mc.column_id IS NOT NULL THEN 'YES' ELSE 'NO' END AS IsMasked,
        mc.masking_function AS MaskingFunction
    FROM sys.columns c
    JOIN sys.types t ON c.user_type_id = t.user_type_id
    LEFT JOIN sys.masked_columns mc ON c.object_id = mc.object_id 
        AND c.column_id = mc.column_id
    WHERE OBJECT_NAME(c.object_id) = 'Customers'
    ORDER BY c.column_id
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Dynamic Data Masking Configuration")


def view_data_as_admin():
    """View customer data as admin (unmasked)"""
    print(f"\n{Fore.YELLOW}To test as ADMIN, please enter admin credentials:{Style.RESET_ALL}")
    username = input("Admin username (default: atelier_admin): ").strip() or "atelier_admin"
    password = input("Admin password: ").strip()
    
    print(f"\n{Fore.GREEN}Connecting as ADMIN (sees real data)...{Style.RESET_ALL}")
    db_admin = DatabaseConnection(username, password, 'admin')
    if db_admin.connect():
        query = """
        SELECT TOP 10
            CustomerID,
            CustomerName,
            Phone,
            Address
        FROM Customers
        ORDER BY CustomerID
        """
        columns, results = db_admin.execute_query(query)
        db_admin.display_results(columns, results, "Customer Data - ADMIN VIEW (Unmasked)")
        db_admin.disconnect()


def view_data_as_cashier():
    """View customer data as cashier (masked)"""
    print(f"\n{Fore.YELLOW}To test as CASHIER, please enter cashier credentials:{Style.RESET_ALL}")
    username = input("Cashier username (default: cashier): ").strip() or "cashier"
    password = input("Cashier password: ").strip()
    
    print(f"\n{Fore.YELLOW}Connecting as CASHIER (sees masked data)...{Style.RESET_ALL}")
    db_cashier = DatabaseConnection(username, password, 'cashier')
    if db_cashier.connect():
        query = """
        SELECT TOP 10
            CustomerID,
            CustomerName,
            Phone,
            Address
        FROM Customers
        ORDER BY CustomerID
        """
        columns, results = db_cashier.execute_query(query)
        db_cashier.display_results(columns, results, "Customer Data - CASHIER VIEW (Masked)")
        db_cashier.disconnect()


def side_by_side_comparison():
    """Show side-by-side comparison of masked vs unmasked data"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print("SIDE-BY-SIDE COMPARISON: Admin vs Cashier View")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    # Admin view
    print(f"{Fore.GREEN}{'─'*40}")
    print("ADMIN VIEW (Unmasked Data)")
    print(f"{'─'*40}{Style.RESET_ALL}")
    view_data_as_admin()
    
    print(f"\n{Fore.YELLOW}{'─'*40}")
    print("CASHIER VIEW (Masked Data)")
    print(f"{'─'*40}{Style.RESET_ALL}")
    view_data_as_cashier()
    
    print(f"\n{Fore.CYAN}{'─'*80}")
    print("EXPLANATION:")
    print(f"{'─'*80}{Style.RESET_ALL}")
    print("• CustomerName: Masked with partial(1, 'XXX', 0) - shows only first letter")
    print("• Phone: Masked with partial(0, 'XXX-XX-', 4) - shows only last 4 digits")
    print("• Address: Masked with default() - completely hidden")
    print(f"\n{Fore.GREEN}Admin and Manager roles have UNMASK permission and see real data.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Cashier and Tailor roles see masked data for privacy protection.{Style.RESET_ALL}")


def test_all_roles():
    """Test DDM with all available roles"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print("TESTING DDM WITH ALL ROLES")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    query = """
    SELECT TOP 5
        CustomerID,
        CustomerName,
        Phone,
        Address
    FROM Customers
    ORDER BY CustomerID
    """
    
    print(f"\n{Fore.YELLOW}This test requires credentials for multiple roles.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}You can skip roles by pressing Enter without username.{Style.RESET_ALL}\n")
    
    roles_info = {
        'admin': ('atelier_admin', 'ADMIN', 'Full access, UNMASK granted', Fore.GREEN),
        'manager': ('manager', 'MANAGER', 'UNMASK granted', Fore.GREEN),
        'cashier': ('cashier', 'CASHIER', 'Sees masked data', Fore.YELLOW),
        'tailor': ('tailor_user', 'TAILOR', 'Sees masked data', Fore.YELLOW)
    }
    
    for role, (default_user, role_name, description, color) in roles_info.items():
        print(f"\n{color}{'─'*80}")
        print(f"{role_name} - {description}")
        print(f"{'─'*80}{Style.RESET_ALL}")
        
        username = input(f"Username (default: {default_user}, Enter to skip): ").strip()
        if not username:
            print(f"{Fore.YELLOW}Skipped {role_name}{Style.RESET_ALL}")
            continue
        if username == "":
            username = default_user
            
        password = input(f"Password for {username}: ").strip()
        
        db = DatabaseConnection(username, password, role)
        if db.connect():
            columns, results = db.execute_query(query)
            if columns and results:
                from tabulate import tabulate
                table_data = [list(row) for row in results]
                print(tabulate(table_data, headers=columns, tablefmt='grid'))
            db.disconnect()
        else:
            print(f"{Fore.RED}Connection failed for {role}{Style.RESET_ALL}")
