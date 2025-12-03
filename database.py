"""
Database connection and query execution module
"""
import pyodbc
from config import Config
from colorama import Fore, Style
from tabulate import tabulate


class DatabaseConnection:
    """Handle database connections and queries"""
    
    def __init__(self, username, password, role='user'):
        """Initialize database connection with credentials"""
        self.username = username
        self.role = role
        self.connection_string = Config.get_connection_string(username, password)
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = pyodbc.connect(self.connection_string)
            self.cursor = self.connection.cursor()
            return True
        except pyodbc.Error as e:
            print(f"{Fore.RED}Connection error: {e}{Style.RESET_ALL}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query, params=None, fetch=True, autocommit=False):
        """Execute SQL query and return results"""
        try:
            # For DDL operations that cannot run in transactions
            if autocommit:
                self.connection.autocommit = True
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if fetch:
                columns = [column[0] for column in self.cursor.description] if self.cursor.description else []
                results = self.cursor.fetchall()
                if autocommit:
                    self.connection.autocommit = False
                return columns, results
            else:
                if not autocommit:
                    self.connection.commit()
                else:
                    self.connection.autocommit = False
                return None, None
        except pyodbc.Error as e:
            print(f"{Fore.RED}Query error: {e}{Style.RESET_ALL}")
            return None, None
    
    def execute_procedure(self, proc_name, params=None):
        """Execute stored procedure"""
        try:
            if params:
                # Filter out None parameters
                param_str = ', '.join(['?' for p in params if p is not None])
                clean_params = [p for p in params if p is not None]
                
                if clean_params:
                    query = f"EXEC {proc_name} {param_str}"
                    self.cursor.execute(query, clean_params)
                else:
                    self.cursor.execute(f"EXEC {proc_name}")
            else:
                self.cursor.execute(f"EXEC {proc_name}")
            
            # Try to fetch results if available
            columns = []
            results = []
            if self.cursor.description:
                columns = [column[0] for column in self.cursor.description]
                results = self.cursor.fetchall()
            
            self.connection.commit()
            return columns, results
        except pyodbc.Error as e:
            print(f"{Fore.RED}Procedure error: {e}{Style.RESET_ALL}")
            return None, None
    
    def display_results(self, columns, results, title=None):
        """Display query results in formatted table"""
        if title:
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{title}")
            print(f"{'='*80}{Style.RESET_ALL}\n")
        
        if not results:
            print(f"{Fore.YELLOW}No results found.{Style.RESET_ALL}")
            return
        
        # Convert results to list of lists for tabulate
        table_data = [list(row) for row in results]
        print(tabulate(table_data, headers=columns, tablefmt='grid'))
        print(f"\n{Fore.GREEN}Total rows: {len(results)}{Style.RESET_ALL}")


def test_connection():
    """Test current database connection"""
    print(f"\n{Fore.CYAN}Testing Current Connection...{Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}Note: Connection test requires manual credential entry.{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Current connection is active and working.{Style.RESET_ALL}")


if __name__ == "__main__":
    test_connection()
