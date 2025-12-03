"""
Atelier Database Management System
Main Application Entry Point
"""
import sys
import os
from colorama import init, Fore, Style

# Initialize colorama for Windows
init(autoreset=True)

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from database import DatabaseConnection, test_connection
from modules.audit import show_audit_menu
from modules.ddm import show_ddm_menu
from modules.extended_events import show_extended_events_menu
from modules.backup import show_backup_menu
from modules.tde import show_tde_menu
from modules.filegroups import show_filegroups_menu
from modules.triggers import show_triggers_menu
from modules.procedures import show_procedures_menu
from modules.views import show_views_menu
from modules.functions import show_functions_menu
from modules.user_management import show_user_management_menu, register_new_user
from modules.two_factor_auth import show_2fa_menu, verify_2fa_login
from config import Config


def print_banner():
    """Display application banner"""
    banner = f"""
{Fore.CYAN}{'='*80}
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║           ATELIER DATABASE MANAGEMENT SYSTEM                          ║
    ║           Security & Functionality Management                         ║
    ║                                                                       ║
    ║           Course Project - Database Security System                   ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
{'='*80}{Style.RESET_ALL}
"""
    print(banner)


def get_user_credentials():
    """Prompt user to enter credentials manually"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print("DATABASE LOGIN - SQL Server Authentication")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Options:{Style.RESET_ALL}")
    print("  1. Login with existing account")
    print("  2. Register new account")
    print("  0. Exit")
    
    option = input(f"\n{Fore.CYAN}Select option: {Style.RESET_ALL}").strip()
    
    if option == '2':
        # Registration process
        if register_new_user():
            print(f"\n{Fore.YELLOW}Please login with existing account or wait for approval.{Style.RESET_ALL}")
            input("Press Enter to continue...")
        return get_user_credentials()  # Return to login
    elif option == '0':
        print(f"{Fore.YELLOW}Exiting application...{Style.RESET_ALL}")
        sys.exit(0)
    
    # Login process
    print(f"\n{Fore.YELLOW}Available roles and suggested usernames:{Style.RESET_ALL}")
    for role, description in Config.ROLES.items():
        suggested_user = Config.SUGGESTED_USERS.get(role, '')
        print(f"  • {Fore.CYAN}{role.upper()}{Style.RESET_ALL} - {description}")
        print(f"    Suggested username: {Fore.GREEN}{suggested_user}{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}Enter your SQL Server credentials:{Style.RESET_ALL}")
    
    username = input(f"{Fore.CYAN}Username: {Style.RESET_ALL}").strip()
    password = input(f"{Fore.CYAN}Password: {Style.RESET_ALL}").strip()
    
    # Determine role based on username (for display purposes)
    role = 'user'
    for r, suggested in Config.SUGGESTED_USERS.items():
        if username.lower() == suggested.lower():
            role = r
            break
    
    return username, password, role


def show_main_menu(is_admin=False):
    """Display main application menu"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print("MAIN MENU - Database Security & Functionality Features")
    print(f"{'='*80}{Style.RESET_ALL}")
    print(f"\n{Fore.GREEN}Security Features:{Style.RESET_ALL}")
    print("  1. Audit - View security events and monitoring")
    print("  2. DDM - Dynamic Data Masking demonstration")
    print("  3. Extended Events - Slow queries & failed logins")
    print("  4. Backup - Automated backup management")
    print("  5. TDE - Transparent Data Encryption status")
    
    print(f"\n{Fore.GREEN}Database Architecture:{Style.RESET_ALL}")
    print("  6. Filegroups - Data distribution across storage")
    
    print(f"\n{Fore.GREEN}Business Logic:{Style.RESET_ALL}")
    print("  7. Triggers - Automated business rules")
    print("  8. Stored Procedures - Business operations")
    print("  9. Views - Reporting & data presentation")
    print(" 10. Functions - Utility calculations")
    
    if is_admin:
        print(f"\n{Fore.MAGENTA}Administration:{Style.RESET_ALL}")
        print(" 11. User Management - Registration & Approvals")
    
    print(f"\n{Fore.MAGENTA}User Settings:{Style.RESET_ALL}")
    print(" 12. Two-Factor Authentication (2FA)")
    
    print(f"\n{Fore.YELLOW}System:{Style.RESET_ALL}")
    if is_admin:
        print(" 13. Test Database Connection")
        print(" 14. Change User Role")
    else:
        print(" 13. Test Database Connection")
        print(" 14. Change User Role")
    print("  0. Exit Application")
    
    print(f"\n{Fore.CYAN}{'─'*80}{Style.RESET_ALL}")


def main():
    """Main application loop"""
    print_banner()
    
    # Get user credentials
    username, password, current_role = get_user_credentials()
    
    # Create database connection
    db = DatabaseConnection(username, password, current_role)
    
    print(f"\n{Fore.CYAN}Connecting to database...{Style.RESET_ALL}")
    
    if not db.connect():
        print(f"\n{Fore.RED}Failed to connect to database!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please check:{Style.RESET_ALL}")
        print("1. SQL Server is running")
        print("2. Database 'Atelier' exists")
        print("3. Username and password are correct")
        print("4. User has permissions to access the database")
        print("5. ODBC Driver 17 for SQL Server is installed")
        input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}✓ Successfully connected to Atelier database!{Style.RESET_ALL}")
    
    # Get current user info and check if admin
    columns, results = db.execute_query("SELECT CURRENT_USER AS CurrentUser, DB_NAME() AS CurrentDB")
    if results:
        print(f"Connected as: {Fore.YELLOW}{results[0][0]}{Style.RESET_ALL} on database: {Fore.YELLOW}{results[0][1]}{Style.RESET_ALL}")
    
    # Check if user is admin (dbo or atelier_admin)
    is_admin = username.lower() in ['atelier_admin', 'sa'] or current_role == 'admin'
    
    # Verify 2FA if enabled
    if not verify_2fa_login(db, username):
        print(f"\n{Fore.RED}2FA verification failed. Access denied.{Style.RESET_ALL}")
        db.disconnect()
        input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
        return
    
    # Main menu loop
    while True:
        show_main_menu(is_admin)
        
        choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
        
        try:
            if choice == '1':
                show_audit_menu(db)
            elif choice == '2':
                show_ddm_menu(db)
            elif choice == '3':
                show_extended_events_menu(db)
            elif choice == '4':
                show_backup_menu(db)
            elif choice == '5':
                show_tde_menu(db)
            elif choice == '6':
                show_filegroups_menu(db)
            elif choice == '7':
                show_triggers_menu(db)
            elif choice == '8':
                show_procedures_menu(db)
            elif choice == '9':
                show_views_menu(db)
            elif choice == '10':
                show_functions_menu(db)
            elif choice == '11' and is_admin:
                show_user_management_menu(db, username, is_admin)
            elif choice == '12':
                show_2fa_menu(db, username)
            elif choice == '13' and not is_admin:
                # Test current connection
                print(f"\n{Fore.CYAN}Testing database connection...{Style.RESET_ALL}")
                try:
                    columns, results = db.execute_query("SELECT @@VERSION AS Version, CURRENT_USER AS CurrentUser, DB_NAME() AS CurrentDatabase")
                    if results:
                        print(f"{Fore.GREEN}✓ Connection is active!{Style.RESET_ALL}")
                        print(f"User: {Fore.YELLOW}{results[0][1]}{Style.RESET_ALL}")
                        print(f"Database: {Fore.YELLOW}{results[0][2]}{Style.RESET_ALL}")
                        print(f"SQL Server Version: {results[0][0][:80]}...")
                    else:
                        print(f"{Fore.RED}✗ Connection test failed{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}✗ Connection error: {e}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Attempting to reconnect...{Style.RESET_ALL}")
                    db.disconnect()
                    if db.connect():
                        print(f"{Fore.GREEN}✓ Reconnected successfully!{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}✗ Reconnection failed{Style.RESET_ALL}")
            elif choice == '13' and is_admin:
                # Test connection for admin
                print(f"\n{Fore.CYAN}Testing database connection...{Style.RESET_ALL}")
                try:
                    columns, results = db.execute_query("SELECT @@VERSION AS Version, CURRENT_USER AS CurrentUser, DB_NAME() AS CurrentDatabase")
                    if results:
                        print(f"{Fore.GREEN}✓ Connection is active!{Style.RESET_ALL}")
                        print(f"User: {Fore.YELLOW}{results[0][1]}{Style.RESET_ALL}")
                        print(f"Database: {Fore.YELLOW}{results[0][2]}{Style.RESET_ALL}")
                        print(f"SQL Server Version: {results[0][0][:80]}...")
                    else:
                        print(f"{Fore.RED}✗ Connection test failed{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}✗ Connection error: {e}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Attempting to reconnect...{Style.RESET_ALL}")
                    db.disconnect()
                    if db.connect():
                        print(f"{Fore.GREEN}✓ Reconnected successfully!{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}✗ Reconnection failed{Style.RESET_ALL}")
            elif choice == '14' and not is_admin:
                # Change user/role for non-admin
                print(f"\n{Fore.CYAN}{'='*80}")
                print("CHANGE USER - Login with different credentials")
                print(f"{'='*80}{Style.RESET_ALL}")
                db.disconnect()
                new_username, new_password, new_role = get_user_credentials()
                db = DatabaseConnection(new_username, new_password, new_role)
                if db.connect():
                    username = new_username
                    password = new_password
                    current_role = new_role
                    is_admin = username.lower() in ['atelier_admin', 'sa'] or current_role == 'admin'
                    print(f"{Fore.GREEN}✓ Successfully logged in!{Style.RESET_ALL}")
                    columns, results = db.execute_query("SELECT CURRENT_USER AS CurrentUser, DB_NAME() AS CurrentDB")
                    if results:
                        print(f"Now connected as: {Fore.YELLOW}{results[0][0]}{Style.RESET_ALL} on database: {Fore.YELLOW}{results[0][1]}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to connect with new credentials!{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Reconnecting with previous credentials...{Style.RESET_ALL}")
                    db = DatabaseConnection(username, password, current_role)
                    if not db.connect():
                        print(f"{Fore.RED}Critical error: Cannot reconnect to database!{Style.RESET_ALL}")
                        break
            elif choice == '14' and is_admin:
                # Change user/role for admin
                print(f"\n{Fore.CYAN}{'='*80}")
                print("CHANGE USER - Login with different credentials")
                print(f"{'='*80}{Style.RESET_ALL}")
                db.disconnect()
                new_username, new_password, new_role = get_user_credentials()
                db = DatabaseConnection(new_username, new_password, new_role)
                if db.connect():
                    username = new_username
                    password = new_password
                    current_role = new_role
                    is_admin = username.lower() in ['atelier_admin', 'sa'] or current_role == 'admin'
                    print(f"{Fore.GREEN}✓ Successfully logged in!{Style.RESET_ALL}")
                    columns, results = db.execute_query("SELECT CURRENT_USER AS CurrentUser, DB_NAME() AS CurrentDB")
                    if results:
                        print(f"Now connected as: {Fore.YELLOW}{results[0][0]}{Style.RESET_ALL} on database: {Fore.YELLOW}{results[0][1]}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to connect with new credentials!{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Reconnecting with previous credentials...{Style.RESET_ALL}")
                    db = DatabaseConnection(username, password, current_role)
                    if not db.connect():
                        print(f"{Fore.RED}Critical error: Cannot reconnect to database!{Style.RESET_ALL}")
                        break
            elif choice == '0':
                print(f"\n{Fore.CYAN}{'='*80}")
                print("Thank you for using Atelier Database Management System!")
                print(f"{'='*80}{Style.RESET_ALL}\n")
                break
            else:
                print(f"{Fore.RED}Invalid option! Please try again.{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Operation interrupted by user.{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Returning to main menu...{Style.RESET_ALL}")
    
    # Cleanup
    db.disconnect()
    print(f"{Fore.GREEN}Database connection closed.{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Application terminated by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
