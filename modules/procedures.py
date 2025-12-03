"""
Stored Procedures Module - Execute and manage stored procedures
"""
from database import DatabaseConnection
from colorama import Fore, Style


def show_procedures_menu(db):
    """Display stored procedures submenu"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}")
        print("STORED PROCEDURES - Business Logic & Operations")
        print(f"{'='*80}{Style.RESET_ALL}")
        print("1. View All Stored Procedures")
        print("2. Execute: sp_CreateOrder (Create Basic Order)")
        print("3. Execute: sp_CreateFullOrder (Create Full Order with Fabrics)")
        print("4. Execute: sp_CalculateOrderCost (Calculate Costs)")
        print("5. Execute: sp_AddPayment (Add Payment)")
        print("6. Execute: sp_TailorReport (Tailor Performance)")
        print("7. Execute: sp_FindAvailableTailors (Find Available)")
        print("8. View Procedure Definitions")
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
        
        if choice == '1':
            view_all_procedures(db)
        elif choice == '2':
            execute_create_order(db)
        elif choice == '3':
            execute_create_full_order(db)
        elif choice == '4':
            execute_calculate_cost(db)
        elif choice == '5':
            execute_add_payment(db)
        elif choice == '6':
            execute_tailor_report(db)
        elif choice == '7':
            execute_find_tailors(db)
        elif choice == '8':
            view_procedure_definitions(db)
        elif choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_all_procedures(db):
    """View all stored procedures in the database"""
    query = """
    SELECT 
        p.name AS ProcedureName,
        p.create_date AS CreatedDate,
        p.modify_date AS ModifiedDate,
        SCHEMA_NAME(p.schema_id) AS SchemaName,
        CASE 
            WHEN p.name LIKE 'sp_Create%' THEN 'Data Manipulation'
            WHEN p.name LIKE 'sp_Calculate%' THEN 'Calculation'
            WHEN p.name LIKE 'sp_%Report%' THEN 'Reporting'
            WHEN p.name LIKE 'sp_Find%' THEN 'Search/Query'
            ELSE 'Other'
        END AS Category
    FROM sys.procedures p
    WHERE p.name LIKE 'sp_%'
        AND SCHEMA_NAME(p.schema_id) = 'dbo'
    ORDER BY Category, p.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Stored Procedures in Atelier Database")


def execute_create_order(db):
    """Execute sp_CreateOrder procedure"""
    print(f"\n{Fore.CYAN}Executing: sp_CreateOrder{Style.RESET_ALL}")
    print("Creates a new order in the system.\n")
    
    # Get available customers
    query_customers = "SELECT TOP 5 CustomerID, CustomerName FROM Customers ORDER BY CustomerID"
    columns, customers = db.execute_query(query_customers)
    
    if not customers:
        print(f"{Fore.RED}No customers found!{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Available Customers:{Style.RESET_ALL}")
    for i, customer in enumerate(customers, 1):
        print(f"{i}. ID: {customer[0]}, Name: {customer[1]}")
    
    # Get available products
    query_products = "SELECT TOP 5 ProductID, ProductName FROM Products ORDER BY ProductID"
    columns, products = db.execute_query(query_products)
    
    print(f"\n{Fore.CYAN}Available Products:{Style.RESET_ALL}")
    for i, product in enumerate(products, 1):
        print(f"{i}. ID: {product[0]}, Name: {product[1]}")
    
    # Get available tailors
    query_tailors = "SELECT TOP 5 TailorID, FullName FROM Tailors ORDER BY TailorID"
    columns, tailors = db.execute_query(query_tailors)
    
    print(f"\n{Fore.CYAN}Available Tailors:{Style.RESET_ALL}")
    for i, tailor in enumerate(tailors, 1):
        print(f"{i}. ID: {tailor[0]}, Name: {tailor[1]}")
    
    # Get input for creating order
    print(f"\n{Fore.YELLOW}Create New Order - Enter Details:{Style.RESET_ALL}")
    try:
        customer_id = input("Customer ID (or press Enter to cancel): ").strip()
        if not customer_id:
            print(f"{Fore.YELLOW}Order creation cancelled.{Style.RESET_ALL}")
            return
        
        product_id = input("Product ID: ").strip()
        tailor_id = input("Tailor ID: ").strip()
        order_date_input = input("Order Date (YYYY-MM-DD, default today): ").strip()
        
        urgency = input("Urgency % (0-100, default 0): ").strip() or "0"
        language = input("Language (default 'Russian'): ").strip() or "Russian"
        status_id = input("Status ID (default 1): ").strip() or "1"
        
        # Execute the procedure
        print(f"\n{Fore.CYAN}Creating order...{Style.RESET_ALL}")
        
        # Get current date if not provided
        if not order_date_input:
            date_query = "SELECT CAST(GETDATE() AS DATE) AS CurrentDate"
            date_cols, date_results = db.execute_query(date_query)
            order_date = date_results[0][0] if date_results else None
        else:
            order_date = order_date_input
        
        query = f"""
        EXEC sp_CreateOrder 
            @OrderDate='{order_date}', 
            @TailorID={tailor_id}, 
            @ProductID={product_id}, 
            @CustomerID={customer_id}, 
            @UrgencyPercentage={urgency}, 
            @Language='{language}', 
            @StatusID={status_id}
        """
        columns, results = db.execute_query(query)
        
        if results:
            new_order_id = results[0][0]
            print(f"{Fore.GREEN}✓ Order created successfully!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Order ID: {new_order_id}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✓ Order created successfully!{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}Error creating order: {e}{Style.RESET_ALL}")


def execute_create_full_order(db):
    """Execute sp_CreateFullOrder procedure with fabrics and complications"""
    print(f"\n{Fore.CYAN}Executing: sp_CreateFullOrder{Style.RESET_ALL}")
    print("Creates a complete order with fabrics and complications.\n")
    
    # Get available customers
    query_customers = "SELECT TOP 5 CustomerID, CustomerName FROM Customers ORDER BY CustomerID"
    columns, customers = db.execute_query(query_customers)
    
    if not customers:
        print(f"{Fore.RED}No customers found!{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Available Customers:{Style.RESET_ALL}")
    for i, customer in enumerate(customers, 1):
        print(f"{i}. ID: {customer[0]}, Name: {customer[1]}")
    
    # Get available products
    query_products = "SELECT TOP 5 ProductID, ProductName FROM Products ORDER BY ProductID"
    columns, products = db.execute_query(query_products)
    
    print(f"\n{Fore.CYAN}Available Products:{Style.RESET_ALL}")
    for i, product in enumerate(products, 1):
        print(f"{i}. ID: {product[0]}, Name: {product[1]}")
    
    # Get available tailors
    query_tailors = "SELECT TOP 5 TailorID, FullName FROM Tailors ORDER BY TailorID"
    columns, tailors = db.execute_query(query_tailors)
    
    print(f"\n{Fore.CYAN}Available Tailors:{Style.RESET_ALL}")
    for i, tailor in enumerate(tailors, 1):
        print(f"{i}. ID: {tailor[0]}, Name: {tailor[1]}")
    
    # Get available fabrics
    query_fabrics = "SELECT TOP 5 FabricID, FabricName, Quantity FROM Fabrics WHERE Quantity > 0 ORDER BY FabricID"
    columns, fabrics = db.execute_query(query_fabrics)
    
    print(f"\n{Fore.CYAN}Available Fabrics (with stock):{Style.RESET_ALL}")
    for i, fabric in enumerate(fabrics, 1):
        print(f"{i}. ID: {fabric[0]}, Name: {fabric[1]}, Stock: {fabric[2]}")
    
    # Get available complications
    query_complications = "SELECT TOP 5 ComplicationID, ComplicationName FROM Complications ORDER BY ComplicationID"
    columns, complications = db.execute_query(query_complications)
    
    print(f"\n{Fore.CYAN}Available Complications:{Style.RESET_ALL}")
    for i, comp in enumerate(complications, 1):
        print(f"{i}. ID: {comp[0]}, Name: {comp[1]}")
    
    # Get input for creating full order
    print(f"\n{Fore.YELLOW}Create Full Order - Enter Details:{Style.RESET_ALL}")
    try:
        customer_id = input("Customer ID (or press Enter to cancel): ").strip()
        if not customer_id:
            print(f"{Fore.YELLOW}Order creation cancelled.{Style.RESET_ALL}")
            return
        
        product_id = input("Product ID: ").strip()
        tailor_id = input("Tailor ID: ").strip()
        order_date_input = input("Order Date (YYYY-MM-DD, default today): ").strip()
        
        urgency = input("Urgency % (0-100, default 0): ").strip() or "0"
        language = input("Language (default 'Russian'): ").strip() or "Russian"
        status_id = input("Status ID (default 1): ").strip() or "1"
        
        # Get fabric list
        fabric_list = input("Fabric List (format: FabricID:Quantity, e.g., '1:5,2:3' or leave empty): ").strip()
        if not fabric_list:
            fabric_list = "NULL"
        else:
            fabric_list = f"'{fabric_list}'"
        
        # Get complication list
        complication_list = input("Complication List (format: ComplicationID, e.g., '1,2,3' or leave empty): ").strip()
        if not complication_list:
            complication_list = "NULL"
        else:
            complication_list = f"'{complication_list}'"
        
        # Execute the procedure
        print(f"\n{Fore.CYAN}Creating full order...{Style.RESET_ALL}")
        
        # Get current date if not provided
        if not order_date_input:
            date_query = "SELECT CAST(GETDATE() AS DATE) AS CurrentDate"
            date_cols, date_results = db.execute_query(date_query)
            order_date = date_results[0][0] if date_results else None
        else:
            order_date = order_date_input
        
        query = f"""
        EXEC sp_CreateFullOrder 
            @OrderDate='{order_date}', 
            @TailorID={tailor_id}, 
            @ProductID={product_id}, 
            @CustomerID={customer_id}, 
            @UrgencyPercentage={urgency}, 
            @Language='{language}', 
            @StatusID={status_id},
            @FabricList={fabric_list},
            @ComplicationList={complication_list}
        """
        columns, results = db.execute_query(query)
        
        if results:
            new_order_id = results[0][0]
            print(f"{Fore.GREEN}✓ Full order created successfully!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Order ID: {new_order_id}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Fabrics and complications have been automatically allocated.{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✓ Order created successfully!{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}Error creating order: {e}{Style.RESET_ALL}")


def execute_calculate_cost(db):
    """Execute sp_CalculateOrderCost procedure"""
    print(f"\n{Fore.CYAN}Executing: sp_CalculateOrderCost{Style.RESET_ALL}")
    print("Calculates total cost for an order including base, fabrics, complications, and urgency.\n")
    
    # Get orders without calculated costs
    query_orders = """
    SELECT TOP 10
        o.OrderID,
        c.CustomerName,
        p.ProductName,
        o.OrderDate,
        CASE WHEN oc.OrderID IS NULL THEN 'Not Calculated' ELSE 'Calculated' END AS CostStatus
    FROM Orders o
    JOIN Customers c ON o.CustomerID = c.CustomerID
    JOIN Products p ON o.ProductID = p.ProductID
    LEFT JOIN OrderCosts oc ON o.OrderID = oc.OrderID
    ORDER BY o.OrderID DESC
    """
    
    columns, results = db.execute_query(query_orders)
    db.display_results(columns, results, "Recent Orders")
    
    if results:
        try:
            order_id = int(input(f"\n{Fore.YELLOW}Enter OrderID to calculate cost (0 to skip): {Style.RESET_ALL}"))
            if order_id > 0:
                print(f"\n{Fore.CYAN}Calculating cost for Order ID: {order_id}...{Style.RESET_ALL}")
                
                # sp_CalculateOrderCost expects @OrderID parameter
                exec_query = f"EXEC sp_CalculateOrderCost @OrderID = {order_id}"
                columns, results = db.execute_query(exec_query, fetch=False)
                
                print(f"{Fore.GREEN}✓ Cost calculation completed!{Style.RESET_ALL}")
                    
                # Show the calculated costs
                query_result = f"""
                SELECT 
                    BaseCost,
                    FabricCost,
                    ComplicationCost,
                    UrgencyCost,
                    BaseCost + FabricCost + ComplicationCost + UrgencyCost AS TotalCost
                FROM OrderCosts
                WHERE OrderID = {order_id}
                """
                columns2, results2 = db.execute_query(query_result)
                if results2:
                    db.display_results(columns2, results2, f"Order {order_id} - Cost Breakdown")
                    
        except ValueError:
            print(f"{Fore.RED}Invalid input!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


def execute_add_payment(db):
    """Execute sp_AddPayment procedure"""
    print(f"\n{Fore.CYAN}Executing: sp_AddPayment{Style.RESET_ALL}")
    print("Adds a payment for an order with validation.\n")
    
    # Get orders that need payment
    query_orders = """
    SELECT TOP 10
        o.OrderID,
        c.CustomerName,
        ISNULL(oc.BaseCost + oc.FabricCost + oc.ComplicationCost + oc.UrgencyCost, 0) AS TotalCost,
        ISNULL(SUM(cr.Amount), 0) AS TotalPaid,
        ISNULL(oc.BaseCost + oc.FabricCost + oc.ComplicationCost + oc.UrgencyCost, 0) - ISNULL(SUM(cr.Amount), 0) AS Balance
    FROM Orders o
    JOIN Customers c ON o.CustomerID = c.CustomerID
    LEFT JOIN OrderCosts oc ON o.OrderID = oc.OrderID
    LEFT JOIN CashRegister cr ON o.OrderID = cr.OrderID
    GROUP BY o.OrderID, c.CustomerName, oc.BaseCost, oc.FabricCost, oc.ComplicationCost, oc.UrgencyCost
    HAVING ISNULL(oc.BaseCost + oc.FabricCost + oc.ComplicationCost + oc.UrgencyCost, 0) - ISNULL(SUM(cr.Amount), 0) > 0
    ORDER BY o.OrderID DESC
    """
    
    columns, results = db.execute_query(query_orders)
    db.display_results(columns, results, "Orders with Outstanding Balance")
    
    if not results:
        print(f"{Fore.YELLOW}No orders with outstanding balance found.{Style.RESET_ALL}")
        return
    
    # Get input for adding payment
    print(f"\n{Fore.YELLOW}Add Payment - Enter Details:{Style.RESET_ALL}")
    try:
        order_id = input("Order ID (or press Enter to cancel): ").strip()
        if not order_id:
            print(f"{Fore.YELLOW}Payment addition cancelled.{Style.RESET_ALL}")
            return
        
        amount = input("Payment Amount: ").strip()
        payment_date_input = input("Payment Date (YYYY-MM-DD, default today): ").strip()
        
        # Execute the procedure
        print(f"\n{Fore.CYAN}Adding payment...{Style.RESET_ALL}")
        
        # Get current date if not provided
        if not payment_date_input:
            date_query = "SELECT CAST(GETDATE() AS DATE) AS CurrentDate"
            date_cols, date_results = db.execute_query(date_query)
            payment_date = date_results[0][0] if date_results else None
        else:
            payment_date = payment_date_input
        
        query = f"""
        EXEC sp_AddPayment 
            @OrderID={order_id}, 
            @PaymentDate='{payment_date}', 
            @Amount={amount}
        """
        columns, results = db.execute_query(query)
        
        # Check if query executed successfully
        # execute_query returns (None, None) on error
        if columns is not None or results is not None:
            print(f"{Fore.GREEN}✓ Payment added successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Payment of {amount} added to Order ID {order_id}{Style.RESET_ALL}")
            print("\nThe procedure includes:")
            print("• Validation that order exists")
            print("• Check that payment doesn't exceed balance")
            print("• Error handling with try-catch")
            print("• Automatic status update via trigger")
            
            print(f"\n{Fore.YELLOW}Note: Only one payment per order per day is allowed.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}To add multiple payments, use different dates or sum amounts.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}✗ Payment failed!{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Possible reasons:{Style.RESET_ALL}")
            print("• Order does not exist")
            print("• Payment amount exceeds outstanding balance")
            print("• Duplicate payment for same date (only one payment per order per day)")
            print("• Invalid data or database constraint violation")
        
    except Exception as e:
        print(f"{Fore.RED}Error adding payment: {e}{Style.RESET_ALL}")


def execute_tailor_report(db):
    """Execute sp_TailorReport procedure"""
    print(f"\n{Fore.CYAN}Executing: sp_TailorReport{Style.RESET_ALL}")
    print("Generates performance report for tailors.\n")
    
    # Get available tailors
    query_tailors = "SELECT TailorID, FullName FROM Tailors ORDER BY TailorID"
    columns, tailors = db.execute_query(query_tailors)
    
    if tailors:
        print(f"{Fore.CYAN}Available Tailors:{Style.RESET_ALL}")
        for tailor in tailors:
            print(f"  {tailor[0]}. {tailor[1]}")
    
    print(f"\n{Fore.YELLOW}Report Parameters:{Style.RESET_ALL}")
    tailor_id_input = input("Tailor ID (leave empty for all tailors): ").strip()
    start_date = input("Start Date (YYYY-MM-DD, leave empty for all time): ").strip()
    end_date = input("End Date (YYYY-MM-DD, leave empty for today): ").strip()
    
    # Prepare parameters
    tailor_id = int(tailor_id_input) if tailor_id_input else None
    
    # Get dates if not provided
    if not start_date:
        start_date = None
    
    if not end_date:
        date_query = "SELECT CAST(GETDATE() AS DATE) AS CurrentDate"
        date_cols, date_results = db.execute_query(date_query)
        end_date = str(date_results[0][0]) if date_results else None
    
    # Execute the procedure
    print(f"\n{Fore.CYAN}Generating report...{Style.RESET_ALL}")
    
    query = f"""
    EXEC sp_TailorReport 
        @TailorID={tailor_id if tailor_id else 'NULL'}, 
        @StartDate={f"'{start_date}'" if start_date else 'NULL'}, 
        @EndDate={f"'{end_date}'" if end_date else 'NULL'}
    """
    
    columns, results = db.execute_query(query)
    
    if results:
        db.display_results(columns, results, "Tailor Performance Report")
        
        print(f"\n{Fore.CYAN}Report Analysis:{Style.RESET_ALL}")
        if len(results) > 0:
            # Assuming columns: TailorID, TailorName, TotalOrders, CompletedOrders, etc.
            print(f"Total tailors in report: {len(results)}")
            if len(results[0]) > 2:
                best_tailor = max(results, key=lambda x: x[2] if len(x) > 2 and x[2] else 0)
                print(f"{Fore.GREEN}Most productive: {best_tailor[1]}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No data available for the specified period.{Style.RESET_ALL}")


def execute_find_tailors(db):
    """Execute sp_FindAvailableTailors procedure"""
    print(f"\n{Fore.CYAN}Executing: sp_FindAvailableTailors{Style.RESET_ALL}")
    print("Finds tailors with lowest workload (most available).\n")
    
    # Get categories first
    query_categories = "SELECT CategoryID, CategoryName FROM Categories"
    columns, categories = db.execute_query(query_categories)
    
    if categories:
        print(f"{Fore.CYAN}Available Categories:{Style.RESET_ALL}")
        for cat in categories:
            print(f"  {cat[0]}. {cat[1]}")
        
        print("\nSearching for available tailors (all categories)...")
    
    # Execute procedure
    columns, results = db.execute_procedure('sp_FindAvailableTailors', [None])
    
    if results:
        db.display_results(columns, results, "Available Tailors (Sorted by Workload)")
        
        print(f"\n{Fore.CYAN}Recommendation:{Style.RESET_ALL}")
        if len(results) > 0:
            print(f"Assign next order to: {Fore.GREEN}{results[0][0]}{Style.RESET_ALL}")
            print(f"Current workload: {results[0][2]} active orders")
    else:
        print(f"{Fore.YELLOW}No tailors found.{Style.RESET_ALL}")


def view_procedure_definitions(db):
    """View stored procedure definitions"""
    query = """
    SELECT 
        p.name AS ProcedureName,
        OBJECT_DEFINITION(p.object_id) AS Definition
    FROM sys.procedures p
    WHERE p.name LIKE 'sp_%'
        AND SCHEMA_NAME(p.schema_id) = 'dbo'
    ORDER BY p.name
    """
    
    columns, results = db.execute_query(query)
    
    if results:
        print(f"\n{Fore.CYAN}Available Stored Procedures:{Style.RESET_ALL}")
        for i, row in enumerate(results, 1):
            print(f"\n{Fore.YELLOW}{i}. {row[0]}{Style.RESET_ALL}")
            definition = row[1][:300] + "..." if len(row[1]) > 300 else row[1]
            print(definition)
    else:
        print(f"{Fore.YELLOW}No stored procedures found.{Style.RESET_ALL}")
