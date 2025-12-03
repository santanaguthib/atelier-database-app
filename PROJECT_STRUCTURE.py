"""
PROJECT STRUCTURE AND FILE DESCRIPTIONS
Atelier Database Management System
"""

# ===================================================================
# ROOT DIRECTORY: c:\AppAppAppAppApp\AtelierApp\
# ===================================================================

PROJECT_STRUCTURE = {
    
    # ===============================================================
    # CONFIGURATION FILES
    # ===============================================================
    
    "config.py": {
        "description": "Database configuration and connection settings",
        "contains": [
            "Config class with database parameters",
            "User roles and credentials management",
            "Connection string generator"
        ],
        "usage": "Import Config to get connection parameters"
    },
    
    ".env.example": {
        "description": "Example environment configuration file",
        "contains": [
            "Database server settings",
            "User credentials templates",
            "Driver configuration"
        ],
        "usage": "Copy to .env and customize for your environment"
    },
    
    ".env": {
        "description": "Actual environment configuration (not in git)",
        "contains": [
            "Real database connection parameters",
            "Actual user passwords",
            "Server-specific settings"
        ],
        "usage": "Created by copying .env.example, contains sensitive data"
    },
    
    # ===============================================================
    # CORE APPLICATION FILES
    # ===============================================================
    
    "main.py": {
        "description": "Main application entry point",
        "contains": [
            "Application banner and UI",
            "Main menu system",
            "Role selection logic",
            "Module navigation"
        ],
        "usage": "Run 'python main.py' to start application"
    },
    
    "database.py": {
        "description": "Database connection and query execution wrapper",
        "contains": [
            "DatabaseConnection class",
            "Query execution methods",
            "Result formatting and display",
            "Connection testing utilities"
        ],
        "usage": "Import DatabaseConnection to interact with SQL Server"
    },
    
    # ===============================================================
    # FUNCTIONAL MODULES (modules/ directory)
    # ===============================================================
    
    "modules/__init__.py": {
        "description": "Modules package initialization",
        "contains": [
            "Package metadata",
            "Module exports",
            "Version information"
        ],
        "usage": "Makes modules/ a Python package"
    },
    
    "modules/audit.py": {
        "description": "Security audit and event monitoring",
        "features": [
            "View server audit status",
            "View audit specifications",
            "Display audit logs",
            "Track failed login attempts",
            "Monitor schema changes"
        ],
        "demonstrates": "SQL Server Audit functionality"
    },
    
    "modules/ddm.py": {
        "description": "Dynamic Data Masking demonstration",
        "features": [
            "View masked columns configuration",
            "Compare data between roles",
            "Side-by-side admin vs cashier view",
            "Test masking with all roles"
        ],
        "demonstrates": "DDM and role-based data protection"
    },
    
    "modules/extended_events.py": {
        "description": "Extended Events monitoring",
        "features": [
            "View active XE sessions",
            "Monitor slow queries (>1 second)",
            "Track failed login events",
            "Create monitoring sessions"
        ],
        "demonstrates": "Performance and security monitoring"
    },
    
    "modules/backup.py": {
        "description": "Backup management and automation",
        "features": [
            "View SQL Agent jobs",
            "Display backup history",
            "Show last backup information",
            "View job schedules",
            "Execute manual backups"
        ],
        "demonstrates": "Automated backup strategy"
    },
    
    "modules/tde.py": {
        "description": "Transparent Data Encryption status",
        "features": [
            "View encryption status",
            "Display master key info",
            "Show certificate details",
            "Monitor encryption progress",
            "List all encrypted databases"
        ],
        "demonstrates": "Data-at-rest encryption with TDE"
    },
    
    "modules/filegroups.py": {
        "description": "Filegroup and data distribution",
        "features": [
            "List all filegroups",
            "View files in filegroups",
            "Show table distribution",
            "Display index distribution",
            "Monitor space usage"
        ],
        "demonstrates": "Database architecture and storage optimization"
    },
    
    "modules/triggers.py": {
        "description": "Trigger automation demonstration",
        "features": [
            "List all triggers",
            "View trigger definitions",
            "Test auto-complete trigger",
            "Test fabric stock validation",
            "Test audit logging trigger"
        ],
        "demonstrates": "Business logic automation with triggers"
    },
    
    "modules/procedures.py": {
        "description": "Stored procedure execution",
        "features": [
            "List all procedures",
            "Execute sp_CreateOrder",
            "Execute sp_CalculateOrderCost",
            "Execute sp_AddPayment",
            "Execute sp_TailorReport",
            "Execute sp_FindAvailableTailors"
        ],
        "demonstrates": "Business operations encapsulation"
    },
    
    "modules/views.py": {
        "description": "View-based reporting",
        "features": [
            "vw_RevenueReport - financial analysis",
            "vw_TailorWorkload - performance metrics",
            "vw_FabricInventory - stock management",
            "vw_OrderDetails - comprehensive info",
            "Role-based views (cashier, tailor)"
        ],
        "demonstrates": "Data presentation and reporting"
    },
    
    "modules/functions.py": {
        "description": "User-defined function testing",
        "features": [
            "fn_GetOrderTotalCost - scalar function",
            "fn_GetPaymentStatus - status calculation",
            "fn_GetCustomerOrderHistory - table-valued",
            "fn_CheckTailorAvailability - availability check"
        ],
        "demonstrates": "Utility calculations and queries"
    },
    
    # ===============================================================
    # DOCUMENTATION FILES
    # ===============================================================
    
    "README.md": {
        "description": "Main project documentation",
        "contains": [
            "Project overview",
            "Feature list",
            "Installation instructions",
            "Usage examples",
            "Troubleshooting guide"
        ],
        "audience": "All users, comprehensive guide"
    },
    
    "QUICKSTART.md": {
        "description": "Quick start guide",
        "contains": [
            "Fast setup steps",
            "Common scenarios",
            "Demo scripts",
            "Quick troubleshooting"
        ],
        "audience": "Users who want to start quickly"
    },
    
    "INSTALL.md": {
        "description": "Detailed installation guide",
        "contains": [
            "Step-by-step installation",
            "ODBC driver setup",
            "Database configuration",
            "Environment setup",
            "Troubleshooting details"
        ],
        "audience": "First-time installers"
    },
    
    "SETUP_CHECKLIST.md": {
        "description": "Pre-deployment checklist",
        "contains": [
            "Requirement verification",
            "Setup steps",
            "Testing procedures",
            "Demo preparation",
            "Common issues and solutions"
        ],
        "audience": "Project presenters, course defense"
    },
    
    # ===============================================================
    # DEPENDENCY FILES
    # ===============================================================
    
    "requirements.txt": {
        "description": "Python package dependencies",
        "packages": [
            "pyodbc - SQL Server connectivity",
            "tabulate - table formatting",
            "colorama - colored console output",
            "python-dotenv - environment variables"
        ],
        "usage": "pip install -r requirements.txt"
    },
    
    ".gitignore": {
        "description": "Git ignore rules",
        "excludes": [
            "Python cache files",
            "Virtual environments",
            ".env file (secrets)",
            "IDE settings",
            "Log files"
        ],
        "usage": "Automatic by git"
    }
}


# ===================================================================
# MODULE DEPENDENCIES AND RELATIONSHIPS
# ===================================================================

MODULE_DEPENDENCIES = """

main.py
│
├─── config.py (configuration)
│    └─── .env (environment variables)
│
├─── database.py (database connection)
│    ├─── config.py
│    ├─── pyodbc (SQL Server driver)
│    ├─── colorama (colored output)
│    └─── tabulate (table formatting)
│
└─── modules/
     │
     ├─── audit.py
     │    └─── database.DatabaseConnection
     │
     ├─── ddm.py
     │    └─── database.DatabaseConnection
     │
     ├─── extended_events.py
     │    └─── database.DatabaseConnection
     │
     ├─── backup.py
     │    └─── database.DatabaseConnection
     │
     ├─── tde.py
     │    └─── database.DatabaseConnection
     │
     ├─── filegroups.py
     │    └─── database.DatabaseConnection
     │
     ├─── triggers.py
     │    └─── database.DatabaseConnection
     │
     ├─── procedures.py
     │    └─── database.DatabaseConnection
     │
     ├─── views.py
     │    └─── database.DatabaseConnection
     │
     └─── functions.py
          └─── database.DatabaseConnection

"""


# ===================================================================
# DATABASE OBJECTS DEMONSTRATED
# ===================================================================

DATABASE_OBJECTS = {
    
    "Tables": [
        "Categories", "Customers", "Tailors", "Products",
        "OrderStatuses", "Orders", "OrderCosts", "OrderComplications",
        "OrderFabrics", "CashRegister", "OrderLogs", "Complications",
        "FabricTypes", "Fabrics"
    ],
    
    "Triggers": [
        "trg_AutoCompleteOrder - Auto-complete on payment",
        "trg_PreventCustomerDelete - Prevent deletion with orders",
        "trg_SetCompletionDate - Auto-set completion date",
        "trg_Orders_Audit - Audit log for orders",
        "trg_CheckFabricStock - Validate fabric availability",
        "trg_PreventCompleteUnpaidOrder - Prevent completion if unpaid"
    ],
    
    "Stored Procedures": [
        "sp_CreateOrder - Create new order",
        "sp_CalculateOrderCost - Calculate costs",
        "sp_AddPayment - Add payment with validation",
        "sp_TailorReport - Performance report",
        "sp_FindAvailableTailors - Find available tailors",
        "sp_CreateFullOrder - Create order with details"
    ],
    
    "Views": [
        "vw_RevenueReport - Monthly revenue",
        "vw_TailorWorkload - Tailor performance",
        "vw_FabricInventory - Fabric stock",
        "vw_OrderDetails - Complete order info",
        "vw_CashierOrders - Cashier view",
        "vw_TailorOrders - Tailor view"
    ],
    
    "Functions": [
        "fn_GetOrderTotalCost - Calculate total",
        "fn_GetPaymentStatus - Payment status",
        "fn_GetCustomerOrderHistory - Customer history",
        "fn_CheckTailorAvailability - Check availability"
    ],
    
    "Security Features": [
        "Server Audit - Security event tracking",
        "DDM - Phone, Address, CustomerName masking",
        "TDE - Database encryption",
        "Extended Events - Performance monitoring",
        "Backup Jobs - Automated backups",
        "Filegroups - Data distribution"
    ],
    
    "Users/Roles": [
        "atelier_admin - Full access (db_owner)",
        "manager - Read/write (db_datareader + db_datawriter)",
        "tailor_user - Limited access (specific tables)",
        "cashier - Read + CashRegister access"
    ]
}


# ===================================================================
# APPLICATION FLOW
# ===================================================================

APPLICATION_FLOW = """

1. START: python main.py
   │
   ├─ Load configuration from .env
   ├─ Initialize colorama for colored output
   └─ Display banner
   
2. USER AUTHENTICATION
   │
   ├─ Display available roles
   ├─ User selects role (admin/manager/tailor/cashier)
   └─ Create DatabaseConnection with selected role
   
3. MAIN MENU LOOP
   │
   ├─ Display main menu with options
   ├─ User selects feature (1-12)
   └─ Navigate to selected module
   
4. MODULE EXECUTION
   │
   ├─ Module displays submenu
   ├─ User selects specific function
   ├─ Execute SQL queries via DatabaseConnection
   ├─ Display results in formatted tables
   └─ Return to module menu or main menu
   
5. EXIT
   │
   ├─ Close database connection
   └─ Display goodbye message

"""


# ===================================================================
# KEY FEATURES DEMONSTRATED
# ===================================================================

KEY_FEATURES = {
    
    "Security": {
        "Audit": "Track all security events and changes",
        "DDM": "Mask sensitive data based on user role",
        "TDE": "Encrypt data at rest",
        "Extended Events": "Monitor security and performance"
    },
    
    "Automation": {
        "Triggers": "Automatic business logic execution",
        "Jobs": "Scheduled backup operations",
        "Procedures": "Encapsulated business operations"
    },
    
    "Architecture": {
        "Filegroups": "Optimized data distribution",
        "Indexes": "Performance optimization",
        "Partitioning": "Logical data separation"
    },
    
    "Reporting": {
        "Views": "Pre-defined data presentations",
        "Functions": "Reusable calculations",
        "Aggregations": "Business intelligence"
    }
}


if __name__ == "__main__":
    print("Atelier Database Management System")
    print("=" * 70)
    print("\nProject Structure Documentation")
    print("\nTotal Files:")
    print(f"  - Core files: 4")
    print(f"  - Module files: 11")
    print(f"  - Documentation files: 5")
    print(f"  - Configuration files: 3")
    print("\nFor detailed information, see individual .md files")
