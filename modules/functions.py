"""
Functions Module - Execute and test utility functions
"""
from database import DatabaseConnection
from colorama import Fore, Style


def show_functions_menu(db):
    """Display functions submenu"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}")
        print("FUNCTIONS - Utility Calculations & Queries")
        print(f"{'='*80}{Style.RESET_ALL}")
        print("1. View All User-Defined Functions")
        print("2. fn_GetOrderTotalCost - Calculate Order Total")
        print("3. fn_GetPaymentStatus - Check Payment Status")
        print("4. fn_GetCustomerOrderHistory - Customer History")
        print("5. fn_CheckTailorAvailability - Tailor Availability")
        print("6. Test All Functions")
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
        
        if choice == '1':
            view_all_functions(db)
        elif choice == '2':
            test_get_order_total_cost(db)
        elif choice == '3':
            test_get_payment_status(db)
        elif choice == '4':
            test_customer_order_history(db)
        elif choice == '5':
            test_tailor_availability(db)
        elif choice == '6':
            test_all_functions(db)
        elif choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_all_functions(db):
    """View all user-defined functions"""
    query = """
    SELECT 
        o.name AS FunctionName,
        o.create_date AS CreatedDate,
        o.modify_date AS ModifiedDate,
        o.type_desc AS FunctionType,
        CASE o.type_desc
            WHEN 'SQL_SCALAR_FUNCTION' THEN 'Returns single value'
            WHEN 'SQL_TABLE_VALUED_FUNCTION' THEN 'Returns table'
            WHEN 'SQL_INLINE_TABLE_VALUED_FUNCTION' THEN 'Returns inline table'
            ELSE 'Other'
        END AS Description
    FROM sys.objects o
    WHERE o.type IN ('FN', 'IF', 'TF')  -- Scalar, Inline Table, Multi-statement Table
        AND SCHEMA_NAME(o.schema_id) = 'dbo'
        AND o.name LIKE 'fn_%'
    ORDER BY o.type_desc, o.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "User-Defined Functions")


def test_get_order_total_cost(db):
    """Test fn_GetOrderTotalCost function"""
    print(f"\n{Fore.CYAN}Function: fn_GetOrderTotalCost{Style.RESET_ALL}")
    print("Purpose: Calculate total cost of an order\n")
    
    # Get some orders
    query_orders = """
    SELECT TOP 10
        o.OrderID,
        c.CustomerName,
        p.ProductName,
        dbo.fn_GetOrderTotalCost(o.OrderID) AS CalculatedTotal
    FROM Orders o
    JOIN Customers c ON o.CustomerID = c.CustomerID
    JOIN Products p ON o.ProductID = p.ProductID
    ORDER BY o.OrderID DESC
    """
    
    columns, results = db.execute_query(query_orders)
    
    if results:
        db.display_results(columns, results, "Orders with Calculated Total Cost")
        
        print(f"\n{Fore.CYAN}Function Details:{Style.RESET_ALL}")
        print("• Returns: DECIMAL(10,2)")
        print("• Calculates: BaseCost + FabricCost + ComplicationCost + UrgencyCost")
        print("• Returns 0 if order has no cost record")
    else:
        print(f"{Fore.YELLOW}No orders available for testing.{Style.RESET_ALL}")


def test_get_payment_status(db):
    """Test fn_GetPaymentStatus function"""
    print(f"\n{Fore.CYAN}Function: fn_GetPaymentStatus{Style.RESET_ALL}")
    print("Purpose: Determine payment status of an order\n")
    
    query = """
    SELECT TOP 15
        o.OrderID,
        c.CustomerName,
        dbo.fn_GetOrderTotalCost(o.OrderID) AS TotalCost,
        ISNULL(SUM(cr.Amount), 0) AS TotalPaid,
        dbo.fn_GetPaymentStatus(o.OrderID) AS PaymentStatus
    FROM Orders o
    JOIN Customers c ON o.CustomerID = c.CustomerID
    LEFT JOIN CashRegister cr ON o.OrderID = cr.OrderID
    GROUP BY o.OrderID, c.CustomerName
    ORDER BY o.OrderID DESC
    """
    
    columns, results = db.execute_query(query)
    
    if results:
        db.display_results(columns, results, "Orders with Payment Status")
        
        # Count by status
        status_counts = {}
        for row in results:
            status = row[4]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n{Fore.CYAN}Payment Status Distribution:{Style.RESET_ALL}")
        for status, count in status_counts.items():
            color = Fore.GREEN if status == 'Fully Paid' else Fore.YELLOW if status == 'Partially Paid' else Fore.RED
            print(f"{color}{status}: {count}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Function Logic:{Style.RESET_ALL}")
        print("• Returns 'Fully Paid' if TotalPaid >= TotalCost")
        print("• Returns 'Partially Paid' if TotalPaid > 0 but < TotalCost")
        print("• Returns 'Unpaid' if TotalPaid = 0")
        print("• Returns 'No Cost Data' if order has no cost record")
    else:
        print(f"{Fore.YELLOW}No orders available for testing.{Style.RESET_ALL}")


def test_customer_order_history(db):
    """Test fn_GetCustomerOrderHistory function"""
    print(f"\n{Fore.CYAN}Function: fn_GetCustomerOrderHistory (Table-Valued){Style.RESET_ALL}")
    print("Purpose: Retrieve complete order history for a customer\n")
    
    # Get customers with orders
    query_customers = """
    SELECT TOP 5
        c.CustomerID,
        c.CustomerName,
        COUNT(o.OrderID) AS OrderCount
    FROM Customers c
    JOIN Orders o ON c.CustomerID = o.CustomerID
    GROUP BY c.CustomerID, c.CustomerName
    ORDER BY COUNT(o.OrderID) DESC
    """
    
    columns, customers = db.execute_query(query_customers)
    
    if customers:
        print(f"{Fore.CYAN}Customers with Orders:{Style.RESET_ALL}")
        db.display_results(columns, customers, "")
        
        # Test with first customer
        customer_id = customers[0][0]
        customer_name = customers[0][1]
        
        print(f"\n{Fore.CYAN}Testing with Customer: {customer_name} (ID: {customer_id}){Style.RESET_ALL}\n")
        
        query_history = f"""
        SELECT 
            OrderID,
            OrderDate,
            ProductName,
            TotalCost,
            StatusName
        FROM dbo.fn_GetCustomerOrderHistory({customer_id})
        ORDER BY OrderDate DESC
        """
        
        columns2, results = db.execute_query(query_history)
        
        if results:
            db.display_results(columns2, results, f"Order History for {customer_name}")
            
            total_spent = sum(row[3] for row in results if row[3])
            print(f"\n{Fore.CYAN}Customer Statistics:{Style.RESET_ALL}")
            print(f"Total Orders: {len(results)}")
            print(f"Total Spent: {Fore.GREEN}{total_spent:,.2f}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No order history found.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No customers with orders found.{Style.RESET_ALL}")


def test_tailor_availability(db):
    """Test fn_CheckTailorAvailability function"""
    print(f"\n{Fore.CYAN}Function: fn_CheckTailorAvailability{Style.RESET_ALL}")
    print("Purpose: Check if a tailor is busy or available\n")
    
    query = """
    SELECT 
        t.TailorID,
        t.FullName,
        COUNT(o.OrderID) AS ActiveOrders,
        CASE dbo.fn_CheckTailorAvailability(t.TailorID)
            WHEN 0 THEN 'Available'
            WHEN 1 THEN 'Busy'
        END AS AvailabilityStatus
    FROM Tailors t
    LEFT JOIN Orders o ON t.TailorID = o.TailorID 
        AND o.StatusID IN (SELECT StatusID FROM OrderStatuses WHERE StatusName != 'Completed')
    GROUP BY t.TailorID, t.FullName
    ORDER BY COUNT(o.OrderID)
    """
    
    columns, results = db.execute_query(query)
    
    if results:
        db.display_results(columns, results, "Tailor Availability Status")
        
        available = sum(1 for r in results if r[3] == 'Available')
        busy = sum(1 for r in results if r[3] == 'Busy')
        
        print(f"\n{Fore.CYAN}Availability Summary:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Available: {available} tailors{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Busy: {busy} tailors{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Function Logic:{Style.RESET_ALL}")
        print("• Returns 1 (Busy) if tailor has 3+ active orders")
        print("• Returns 0 (Available) if tailor has < 3 active orders")
        print("• Helps with workload balancing")
    else:
        print(f"{Fore.YELLOW}No tailors found.{Style.RESET_ALL}")


def test_all_functions(db):
    """Test all functions in sequence"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print("TESTING ALL FUNCTIONS")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}1. Testing fn_GetOrderTotalCost...{Style.RESET_ALL}")
    test_get_order_total_cost(db)
    
    input(f"\n{Fore.YELLOW}Press Enter to continue to next function...{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}2. Testing fn_GetPaymentStatus...{Style.RESET_ALL}")
    test_get_payment_status(db)
    
    input(f"\n{Fore.YELLOW}Press Enter to continue to next function...{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}3. Testing fn_GetCustomerOrderHistory...{Style.RESET_ALL}")
    test_customer_order_history(db)
    
    input(f"\n{Fore.YELLOW}Press Enter to continue to next function...{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}4. Testing fn_CheckTailorAvailability...{Style.RESET_ALL}")
    test_tailor_availability(db)
    
    print(f"\n{Fore.GREEN}{'='*80}")
    print("ALL FUNCTIONS TESTED SUCCESSFULLY")
    print(f"{'='*80}{Style.RESET_ALL}")
