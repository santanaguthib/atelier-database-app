"""
Triggers Module - Test and manage business logic automation
"""
from database import DatabaseConnection
from colorama import Fore, Style


def show_triggers_menu(db):
    """Display triggers submenu"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}")
        print("TRIGGERS - Business Logic Automation")
        print(f"{'='*80}{Style.RESET_ALL}")
        print("1. View All Triggers")
        print("2. View Trigger Definitions")
        print("3. Test Auto-Complete Order Trigger")
        print("4. Test Fabric Stock Check Trigger")
        print("5. Test Order Audit Log Trigger")
        print("6. Test Prevent Delete Customer Trigger")
        print("7. View Trigger Execution History")
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
        
        if choice == '1':
            view_all_triggers(db)
        elif choice == '2':
            view_trigger_definitions(db)
        elif choice == '3':
            test_autocomplete_trigger(db)
        elif choice == '4':
            test_fabric_stock_trigger(db)
        elif choice == '5':
            test_audit_log_trigger(db)
        elif choice == '6':
            test_prevent_delete_trigger(db)
        elif choice == '7':
            view_trigger_history(db)
        elif choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_all_triggers(db):
    """View all triggers in the database"""
    query = """
    SELECT 
        t.name AS TriggerName,
        OBJECT_NAME(t.parent_id) AS TableName,
        t.create_date AS CreatedDate,
        t.modify_date AS ModifiedDate,
        CASE t.is_disabled
            WHEN 0 THEN 'Enabled'
            ELSE 'Disabled'
        END AS Status,
        te.type_desc AS TriggerEvent
    FROM sys.triggers t
    LEFT JOIN sys.trigger_events te ON t.object_id = te.object_id
    WHERE t.parent_class = 1  -- Table triggers only
    ORDER BY OBJECT_NAME(t.parent_id), t.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "All Triggers in Database")


def view_trigger_definitions(db):
    """View trigger definitions (code)"""
    query = """
    SELECT 
        t.name AS TriggerName,
        OBJECT_NAME(t.parent_id) AS TableName,
        OBJECT_DEFINITION(t.object_id) AS TriggerDefinition
    FROM sys.triggers t
    WHERE t.parent_class = 1
    ORDER BY OBJECT_NAME(t.parent_id), t.name
    """
    columns, results = db.execute_query(query)
    
    if results:
        for row in results:
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"Trigger: {row[0]} on table {row[1]}")
            print(f"{'='*80}{Style.RESET_ALL}")
            print(row[2][:500] + "..." if len(row[2]) > 500 else row[2])
    else:
        print(f"{Fore.YELLOW}No triggers found.{Style.RESET_ALL}")


def test_autocomplete_trigger(db):
    """Test automatic order completion when fully paid"""
    print(f"\n{Fore.CYAN}Testing: trg_AutoCompleteOrder{Style.RESET_ALL}")
    print("This trigger automatically marks orders as 'Completed' when fully paid.\n")
    
    # First, get an order that's not completed
    query_order = """
    SELECT TOP 1 
        o.OrderID,
        o.StatusID,
        os.StatusName,
        ISNULL(SUM(cr.Amount), 0) AS TotalPaid,
        ISNULL(oc.BaseCost + oc.FabricCost + oc.ComplicationCost + oc.UrgencyCost, 0) AS TotalCost
    FROM Orders o
    LEFT JOIN OrderStatuses os ON o.StatusID = os.StatusID
    LEFT JOIN CashRegister cr ON o.OrderID = cr.OrderID
    LEFT JOIN OrderCosts oc ON o.OrderID = oc.OrderID
    WHERE os.StatusName != 'Completed'
    GROUP BY o.OrderID, o.StatusID, os.StatusName, oc.BaseCost, oc.FabricCost, 
             oc.ComplicationCost, oc.UrgencyCost
    HAVING ISNULL(SUM(cr.Amount), 0) < ISNULL(oc.BaseCost + oc.FabricCost + oc.ComplicationCost + oc.UrgencyCost, 999999)
    """
    
    columns, results = db.execute_query(query_order)
    
    if not results:
        print(f"{Fore.YELLOW}No suitable test orders found (all orders are completed or fully paid).{Style.RESET_ALL}")
        return
    
    order_id = results[0][0]
    status_name = results[0][2]
    total_paid = results[0][3]
    total_cost = results[0][4]
    
    print(f"Order ID: {order_id}")
    print(f"Current Status: {status_name}")
    print(f"Total Cost: {total_cost:.2f}")
    print(f"Total Paid: {total_paid:.2f}")
    print(f"Remaining: {total_cost - total_paid:.2f}")
    
    if total_cost - total_paid <= 0:
        print(f"\n{Fore.GREEN}This order is fully paid!{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.YELLOW}Add payment to complete this order?{Style.RESET_ALL}")
    confirm = input("Enter payment amount (or press Enter to skip): ").strip()
    
    if confirm:
        try:
            amount = float(confirm)
            remaining = total_cost - total_paid
            
            if amount > remaining:
                print(f"{Fore.YELLOW}Payment amount exceeds balance. Adjusting to {remaining:.2f}{Style.RESET_ALL}")
                amount = remaining
            
            # Add payment using sp_AddPayment procedure
            query = f"EXEC sp_AddPayment @OrderID={order_id}, @PaymentDate=GETDATE(), @Amount={amount}"
            db.execute_query(query)
            
            print(f"{Fore.GREEN}✓ Payment of {amount:.2f} added successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}The trigger will automatically update order status if fully paid.{Style.RESET_ALL}")
            
        except ValueError:
            print(f"{Fore.RED}Invalid amount entered.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error adding payment: {e}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Payment skipped.{Style.RESET_ALL}")


def test_fabric_stock_trigger(db):
    """Test fabric stock validation trigger"""
    print(f"\n{Fore.CYAN}Testing: trg_CheckFabricStock{Style.RESET_ALL}")
    print("This trigger prevents fabric allocation if insufficient stock.\n")
    
    # Get available fabrics
    query_fabric = """
    SELECT TOP 5
        FabricID,
        FabricName,
        Quantity AS AvailableQuantity
    FROM Fabrics
    WHERE Quantity > 0
    ORDER BY Quantity
    """
    
    columns, results = db.execute_query(query_fabric)
    db.display_results(columns, results, "Available Fabrics with Stock")
    
    print(f"\n{Fore.CYAN}Trigger Behavior:{Style.RESET_ALL}")
    print("• BEFORE INSERT: Checks if requested fabric quantity is available")
    print("• If insufficient stock: Transaction is rolled back with error message")
    print("• If sufficient stock: Fabric quantity is decremented automatically")
    print("• Ensures data integrity and prevents overselling")


def test_audit_log_trigger(db):
    """Test order audit logging trigger"""
    print(f"\n{Fore.CYAN}Testing: trg_Orders_Audit{Style.RESET_ALL}")
    print("This trigger automatically logs all changes to Orders table.\n")
    
    # View recent audit logs
    query_logs = """
    SELECT TOP 20
        LogID,
        OrderID,
        OperationType,
        OperationDate,
        UserName
    FROM OrderLogs
    ORDER BY OperationDate DESC
    """
    
    columns, results = db.execute_query(query_logs)
    db.display_results(columns, results, "Recent Order Audit Logs")
    
    print(f"\n{Fore.CYAN}Trigger Behavior:{Style.RESET_ALL}")
    print("• Captures INSERT, UPDATE, and DELETE operations")
    print("• Records: OrderID, Action type, Timestamp, Username")
    print("• Stores old and new values for audit trail")
    print("• Executes automatically after each data modification")


def test_prevent_delete_trigger(db):
    """Test prevent customer deletion trigger"""
    print(f"\n{Fore.CYAN}Testing: trg_PreventCustomerDelete{Style.RESET_ALL}")
    print("This trigger prevents deletion of customers with active orders.\n")
    
    # Find customers with orders
    query_customers = """
    SELECT TOP 10
        c.CustomerID,
        c.CustomerName,
        COUNT(o.OrderID) AS ActiveOrders,
        MAX(o.OrderDate) AS LastOrderDate
    FROM Customers c
    LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
    GROUP BY c.CustomerID, c.CustomerName
    HAVING COUNT(o.OrderID) > 0
    ORDER BY COUNT(o.OrderID) DESC
    """
    
    columns, results = db.execute_query(query_customers)
    db.display_results(columns, results, "Customers with Active Orders (Protected from Deletion)")
    
    print(f"\n{Fore.CYAN}Trigger Behavior:{Style.RESET_ALL}")
    print("• INSTEAD OF DELETE trigger")
    print("• Checks if customer has any orders in the system")
    print("• If orders exist: Prevents deletion and raises error")
    print("• If no orders: Allows deletion to proceed")
    print("• Maintains referential integrity and historical data")
    
    # Show customers without orders (can be deleted)
    query_safe = """
    SELECT TOP 5
        c.CustomerID,
        c.CustomerName,
        COUNT(o.OrderID) AS OrderCount
    FROM Customers c
    LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
    GROUP BY c.CustomerID, c.CustomerName
    HAVING COUNT(o.OrderID) = 0
    """
    
    columns2, results2 = db.execute_query(query_safe)
    if results2:
        print(f"\n{Fore.GREEN}Customers without orders (can be safely deleted):{Style.RESET_ALL}")
        db.display_results(columns2, results2, "")
    else:
        print(f"\n{Fore.YELLOW}All customers have orders - none can be deleted.{Style.RESET_ALL}")


def view_trigger_history(db):
    """View trigger execution statistics"""
    print(f"\n{Fore.CYAN}Trigger Execution Statistics{Style.RESET_ALL}\n")
    
    # This is simulated since SQL Server doesn't track trigger execution history directly
    print("Checking OrderLogs for trigger activity...")
    
    query = """
    SELECT 
        OperationType,
        COUNT(*) AS ExecutionCount,
        MIN(OperationDate) AS FirstExecution,
        MAX(OperationDate) AS LastExecution
    FROM OrderLogs
    GROUP BY OperationType
    ORDER BY COUNT(*) DESC
    """
    
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Audit Log Trigger Activity Summary")
    
    print(f"\n{Fore.CYAN}Note:{Style.RESET_ALL}")
    print("SQL Server doesn't provide built-in trigger execution statistics.")
    print("This data is derived from audit logs created by the trg_Orders_Audit trigger.")
