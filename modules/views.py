"""
Views Module - Access reporting and analytical views
"""
from database import DatabaseConnection
from colorama import Fore, Style


def show_views_menu(db):
    """Display views submenu"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}")
        print("VIEWS - Reporting & Data Presentation")
        print(f"{'='*80}{Style.RESET_ALL}")
        print("1. View All Views in Database")
        print("2. vw_RevenueReport - Monthly Revenue Analysis")
        print("3. vw_TailorWorkload - Tailor Performance")
        print("4. vw_FabricInventory - Fabric Stock Status")
        print("5. vw_OrderDetails - Complete Order Information")
        print("6. vw_CashierOrders - Orders with Payments")
        print("7. vw_TailorOrders - Tailor's Personal Orders")
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
        
        if choice == '1':
            view_all_views(db)
        elif choice == '2':
            view_revenue_report(db)
        elif choice == '3':
            view_tailor_workload(db)
        elif choice == '4':
            view_fabric_inventory(db)
        elif choice == '5':
            view_order_details(db)
        elif choice == '6':
            view_cashier_orders(db)
        elif choice == '7':
            view_tailor_orders(db)
        elif choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_all_views(db):
    """View all views in the database"""
    query = """
    SELECT 
        v.name AS ViewName,
        v.create_date AS CreatedDate,
        v.modify_date AS ModifiedDate,
        SCHEMA_NAME(v.schema_id) AS SchemaName,
        CASE 
            WHEN v.name LIKE '%Revenue%' THEN 'Financial'
            WHEN v.name LIKE '%Tailor%' THEN 'HR/Workload'
            WHEN v.name LIKE '%Fabric%' THEN 'Inventory'
            WHEN v.name LIKE '%Order%' THEN 'Operations'
            WHEN v.name LIKE '%Cashier%' THEN 'Role-Based'
            ELSE 'Other'
        END AS Category
    FROM sys.views v
    WHERE SCHEMA_NAME(v.schema_id) = 'dbo'
        AND v.name LIKE 'vw_%'
    ORDER BY Category, v.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Views in Atelier Database")


def view_revenue_report(db):
    """Query vw_RevenueReport view"""
    print(f"\n{Fore.CYAN}View: vw_RevenueReport{Style.RESET_ALL}")
    print("Purpose: Monthly revenue analysis with aggregated payment data\n")
    
    query = """
    SELECT 
        Year,
        Month,
        MonthName,
        OrdersCount,
        TotalRevenue,
        AvgOrderAmount
    FROM vw_RevenueReport
    ORDER BY Year DESC, Month DESC
    """
    
    columns, results = db.execute_query(query)
    
    if results:
        db.display_results(columns, results, "Monthly Revenue Report")
        
        # Calculate totals
        total_revenue = sum(row[3] for row in results if row[3])
        total_orders = sum(row[4] for row in results if row[4])
        
        print(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
        print(f"Total Revenue: {Fore.GREEN}{total_revenue:,.2f}{Style.RESET_ALL}")
        print(f"Total Orders: {Fore.GREEN}{total_orders}{Style.RESET_ALL}")
        if total_orders > 0:
            print(f"Average per Order: {Fore.GREEN}{total_revenue/total_orders:,.2f}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No revenue data available.{Style.RESET_ALL}")


def view_tailor_workload(db):
    """Query vw_TailorWorkload view"""
    print(f"\n{Fore.CYAN}View: vw_TailorWorkload{Style.RESET_ALL}")
    print("Purpose: Analyze tailor performance and workload distribution\n")
    
    query = """
    SELECT 
        FullName AS TailorName,
        CategoryName,
        ActiveOrders,
        CompletedOrders,
        AvgDaysToComplete
    FROM vw_TailorWorkload
    ORDER BY ActiveOrders DESC
    """
    
    columns, results = db.execute_query(query)
    
    if results:
        db.display_results(columns, results, "Tailor Workload Analysis")
        
        print(f"\n{Fore.CYAN}Performance Metrics:{Style.RESET_ALL}")
        
        # Find best performers
        if len(results) > 0:
            most_orders = max(results, key=lambda x: x[2] if x[2] else 0)
            fastest = min((r for r in results if r[4]), key=lambda x: x[4], default=None)
            
            print(f"Most productive: {Fore.GREEN}{most_orders[0]}{Style.RESET_ALL} ({most_orders[2]} orders)")
            if fastest:
                print(f"Fastest completion: {Fore.GREEN}{fastest[0]}{Style.RESET_ALL} ({fastest[4]:.1f} days avg)")
    else:
        print(f"{Fore.YELLOW}No tailor workload data available.{Style.RESET_ALL}")


def view_fabric_inventory(db):
    """Query vw_FabricInventory view"""
    print(f"\n{Fore.CYAN}View: vw_FabricInventory{Style.RESET_ALL}")
    print("Purpose: Monitor fabric stock levels with alerts\n")
    
    query = """
    SELECT 
        FabricName,
        FabricTypeName,
        Quantity,
        Unit,
        Price,
        StockStatus
    FROM vw_FabricInventory
    ORDER BY 
        CASE StockStatus
            WHEN 'Critical stock' THEN 1
            WHEN 'Low stock' THEN 2
            WHEN 'Normal stock' THEN 3
        END,
        FabricName
    """
    
    columns, results = db.execute_query(query)
    
    if results:
        db.display_results(columns, results, "Fabric Inventory Status")
        
        # Stock analysis
        out_of_stock = sum(1 for r in results if r[5] == 'OUT OF STOCK')
        low_stock = sum(1 for r in results if r[5] == 'LOW STOCK')
        in_stock = sum(1 for r in results if r[5] == 'IN STOCK')
        
        print(f"\n{Fore.CYAN}Inventory Status:{Style.RESET_ALL}")
        if out_of_stock > 0:
            print(f"{Fore.RED}⚠ OUT OF STOCK: {out_of_stock} items{Style.RESET_ALL}")
        if low_stock > 0:
            print(f"{Fore.YELLOW}⚠ LOW STOCK: {low_stock} items{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ IN STOCK: {in_stock} items{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No fabric inventory data available.{Style.RESET_ALL}")


def view_order_details(db):
    """Query vw_OrderDetails view"""
    print(f"\n{Fore.CYAN}View: vw_OrderDetails{Style.RESET_ALL}")
    print("Purpose: Comprehensive order information with all related data\n")
    
    query = """
    SELECT TOP 20
        OrderID,
        OrderDate,
        CustomerName,
        Phone,
        TailorName,
        ProductName,
        StatusName,
        TotalCost,
        PaidAmount,
        RemainingAmount
    FROM vw_OrderDetails
    ORDER BY OrderDate DESC
    """
    
    columns, results = db.execute_query(query)
    
    if results:
        db.display_results(columns, results, "Detailed Order Information (Last 20)")
        
        # Payment status analysis
        fully_paid = sum(1 for r in results if r[9] == 0)
        partially_paid = sum(1 for r in results if r[9] > 0 and r[8] > 0)
        unpaid = sum(1 for r in results if r[8] == 0)
        
        print(f"\n{Fore.CYAN}Payment Status:{Style.RESET_ALL}")
        print(f"Fully Paid: {Fore.GREEN}{fully_paid}{Style.RESET_ALL}")
        print(f"Partially Paid: {Fore.YELLOW}{partially_paid}{Style.RESET_ALL}")
        print(f"Unpaid: {Fore.RED}{unpaid}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No order details available.{Style.RESET_ALL}")


def view_cashier_orders(db):
    """Query vw_CashierOrders view"""
    print(f"\n{Fore.CYAN}View: vw_CashierOrders{Style.RESET_ALL}")
    print("Purpose: Orders with payment information (Cashier's view)\n")
    
    query = """
    SELECT 
        OrderID,
        OrderDate,
        CustomerName,
        PaymentDate,
        Amount
    FROM vw_CashierOrders
    ORDER BY PaymentDate DESC
    """
    
    columns, results = db.execute_query(query)
    
    if results:
        db.display_results(columns, results, "Cashier Orders View - Paid Orders")
        
        total_collected = sum(row[4] for row in results if row[4])
        print(f"\n{Fore.CYAN}Total Collected: {Fore.GREEN}{total_collected:,.2f}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No payment records found.{Style.RESET_ALL}")


def view_tailor_orders(db):
    """Query vw_TailorOrders view"""
    print(f"\n{Fore.CYAN}View: vw_TailorOrders{Style.RESET_ALL}")
    print("Purpose: Orders assigned to tailors (Tailor's personal view)\n")
    
    query = """
    SELECT 
        OrderID,
        OrderDate,
        TailorName,
        CustomerName,
        StatusID
    FROM vw_TailorOrders
    ORDER BY OrderDate DESC
    """
    
    columns, results = db.execute_query(query)
    
    if results:
        db.display_results(columns, results, "Tailor Orders View - Assigned Orders")
        
        print(f"\n{Fore.CYAN}Note:{Style.RESET_ALL}")
        print("This view would normally filter by current tailor's ID.")
        print("It shows only orders assigned to the logged-in tailor.")
    else:
        print(f"{Fore.YELLOW}No orders found.{Style.RESET_ALL}")
