"""
Two-Factor Authentication Module - Google Authenticator Integration
"""

import pyotp
import qrcode
import os
from colorama import Fore, Style
from datetime import datetime


def show_2fa_menu(db, current_user):
    """Main menu for 2FA management"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}TWO-FACTOR AUTHENTICATION (2FA) - Google Authenticator{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        # Check if user has 2FA enabled
        is_enabled = check_2fa_status(db, current_user)
        
        if is_enabled:
            print(f"{Fore.GREEN}✓ 2FA is currently ENABLED{Style.RESET_ALL}")
            print("1. Disable 2FA")
            print("2. View Backup Codes")
            print("3. Regenerate Backup Codes")
            print("4. Test 2FA Code")
        else:
            print(f"{Fore.YELLOW}✗ 2FA is currently DISABLED{Style.RESET_ALL}")
            print("1. Enable 2FA (Setup Google Authenticator)")
            print("2. View 2FA Information")
        
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.CYAN}Select option: {Style.RESET_ALL}").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            if is_enabled:
                disable_2fa(db, current_user)
            else:
                enable_2fa(db, current_user)
        elif choice == '2':
            if is_enabled:
                view_backup_codes(db, current_user)
            else:
                show_2fa_info()
        elif choice == '3' and is_enabled:
            regenerate_backup_codes(db, current_user)
        elif choice == '4' and is_enabled:
            test_2fa_code(db, current_user)
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")


def check_2fa_status(db, username):
    """Check if user has 2FA enabled"""
    query = """
    SELECT IsEnabled 
    FROM TwoFactorAuth 
    WHERE UserID = (SELECT principal_id FROM sys.database_principals WHERE name = ?)
    """
    
    columns, results = db.execute_query(query, params=(username,))
    
    if results and len(results) > 0:
        return bool(results[0][0])
    return False


def get_user_secret(db, username):
    """Get user's 2FA secret key"""
    query = """
    SELECT SecretKey, BackupCodes
    FROM TwoFactorAuth 
    WHERE UserID = (SELECT principal_id FROM sys.database_principals WHERE name = ?)
    """
    
    columns, results = db.execute_query(query, params=(username,))
    
    if results and len(results) > 0:
        return results[0][0], results[0][1]
    return None, None


def enable_2fa(db, username):
    """Enable 2FA for user - setup Google Authenticator"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}ENABLE TWO-FACTOR AUTHENTICATION{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    # Generate secret key
    secret = pyotp.random_base32()
    
    # Generate backup codes
    backup_codes = generate_backup_codes()
    backup_codes_str = ','.join(backup_codes)
    
    # Create TOTP object
    totp = pyotp.TOTP(secret)
    
    # Generate provisioning URI for QR code
    provisioning_uri = totp.provisioning_uri(
        name=username,
        issuer_name="Atelier Database"
    )
    
    # Create QR codes directory if it doesn't exist
    qr_dir = "2FA_QRCodes"
    if not os.path.exists(qr_dir):
        os.makedirs(qr_dir)
    
    # Generate QR code and save as PNG
    qr_filename = os.path.join(qr_dir, f"2FA_QR_{username}.png")
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_filename)
    
    print(f"{Fore.GREEN}✓ QR Code generated and saved as: {qr_filename}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Setup Instructions:{Style.RESET_ALL}")
    print("1. Open Google Authenticator app on your phone")
    print("2. Tap '+' to add a new account")
    print("3. Choose 'Scan QR code' and scan the generated PNG file")
    print(f"   (File location: {os.path.abspath(qr_filename)})")
    print("\n   OR manually enter this secret key:")
    print(f"   {Fore.GREEN}{secret}{Style.RESET_ALL}")
    print(f"\n4. After adding, enter the 6-digit code from the app to verify:\n")
    
    # Verify setup
    for attempt in range(3):
        code = input(f"{Fore.CYAN}Enter 6-digit code from Google Authenticator: {Style.RESET_ALL}").strip()
        
        if totp.verify(code):
            # Save to database
            user_id_query = "SELECT principal_id FROM sys.database_principals WHERE name = ?"
            columns, user_results = db.execute_query(user_id_query, params=(username,))
            
            if not user_results:
                print(f"{Fore.RED}Error: User not found!{Style.RESET_ALL}")
                return
            
            user_id = user_results[0][0]
            
            # Check if record exists
            check_query = "SELECT COUNT(*) FROM TwoFactorAuth WHERE UserID = ?"
            columns, check_results = db.execute_query(check_query, params=(user_id,))
            
            if check_results[0][0] > 0:
                # Update existing record
                update_query = """
                UPDATE TwoFactorAuth 
                SET SecretKey = ?, IsEnabled = 1, BackupCodes = ?, CreatedAt = GETDATE()
                WHERE UserID = ?
                """
                db.execute_query(update_query, params=(secret, backup_codes_str, user_id), fetch=False, autocommit=True)
            else:
                # Insert new record
                insert_query = """
                INSERT INTO TwoFactorAuth (UserID, SecretKey, IsEnabled, BackupCodes, CreatedAt)
                VALUES (?, ?, 1, ?, GETDATE())
                """
                db.execute_query(insert_query, params=(user_id, secret, backup_codes_str), fetch=False, autocommit=True)
            
            print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ TWO-FACTOR AUTHENTICATION ENABLED SUCCESSFULLY!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")
            
            print(f"{Fore.YELLOW}⚠ IMPORTANT: Save these backup codes in a safe place!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}You can use them if you lose access to your phone.{Style.RESET_ALL}\n")
            
            print(f"{Fore.CYAN}Backup Codes:{Style.RESET_ALL}")
            for i, code in enumerate(backup_codes, 1):
                print(f"  {i:2d}. {code}")
            
            print(f"\n{Fore.GREEN}From now on, you'll need to enter a code from Google Authenticator when logging in.{Style.RESET_ALL}")
            
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        else:
            print(f"{Fore.RED}✗ Invalid code! {2 - attempt} attempts remaining.{Style.RESET_ALL}")
    
    print(f"\n{Fore.RED}✗ Setup failed. Too many invalid attempts.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Please try again later.{Style.RESET_ALL}")
    
    # Delete QR code file if setup failed
    if os.path.exists(qr_filename):
        os.remove(qr_filename)


def disable_2fa(db, username):
    """Disable 2FA for user"""
    print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}DISABLE TWO-FACTOR AUTHENTICATION{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")
    
    print(f"{Fore.RED}Warning: Disabling 2FA will reduce your account security!{Style.RESET_ALL}\n")
    
    confirm = input(f"{Fore.CYAN}Are you sure you want to disable 2FA? (yes/no): {Style.RESET_ALL}").strip().lower()
    
    if confirm != 'yes':
        print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
        return
    
    # Verify with current 2FA code
    secret, _ = get_user_secret(db, username)
    if not secret:
        print(f"{Fore.RED}Error: 2FA not properly configured!{Style.RESET_ALL}")
        return
    
    code = input(f"\n{Fore.CYAN}Enter current 6-digit code from Google Authenticator: {Style.RESET_ALL}").strip()
    
    totp = pyotp.TOTP(secret)
    if not totp.verify(code):
        print(f"{Fore.RED}✗ Invalid code! Cannot disable 2FA.{Style.RESET_ALL}")
        return
    
    # Disable in database
    user_id_query = "SELECT principal_id FROM sys.database_principals WHERE name = ?"
    columns, user_results = db.execute_query(user_id_query, params=(username,))
    
    if not user_results:
        print(f"{Fore.RED}Error: User not found!{Style.RESET_ALL}")
        return
    
    user_id = user_results[0][0]
    
    update_query = "UPDATE TwoFactorAuth SET IsEnabled = 0 WHERE UserID = ?"
    db.execute_query(update_query, params=(user_id,), fetch=False, autocommit=True)
    
    print(f"\n{Fore.GREEN}✓ Two-Factor Authentication has been disabled.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}You can re-enable it anytime from the 2FA menu.{Style.RESET_ALL}")


def view_backup_codes(db, username):
    """View user's backup codes"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}BACKUP CODES{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    _, backup_codes_str = get_user_secret(db, username)
    
    if not backup_codes_str:
        print(f"{Fore.RED}No backup codes found!{Style.RESET_ALL}")
        return
    
    backup_codes = backup_codes_str.split(',')
    
    print(f"{Fore.YELLOW}Use these codes if you lose access to your phone:{Style.RESET_ALL}\n")
    
    for i, code in enumerate(backup_codes, 1):
        print(f"  {i:2d}. {code}")
    
    print(f"\n{Fore.YELLOW}⚠ Keep these codes in a safe place!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Each code can only be used once.{Style.RESET_ALL}")
    
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")


def regenerate_backup_codes(db, username):
    """Generate new backup codes"""
    print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}REGENERATE BACKUP CODES{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")
    
    print(f"{Fore.RED}Warning: Old backup codes will no longer work!{Style.RESET_ALL}\n")
    
    confirm = input(f"{Fore.CYAN}Generate new backup codes? (yes/no): {Style.RESET_ALL}").strip().lower()
    
    if confirm != 'yes':
        print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
        return
    
    # Generate new codes
    new_codes = generate_backup_codes()
    new_codes_str = ','.join(new_codes)
    
    # Update database
    user_id_query = "SELECT principal_id FROM sys.database_principals WHERE name = ?"
    columns, user_results = db.execute_query(user_id_query, params=(username,))
    
    if not user_results:
        print(f"{Fore.RED}Error: User not found!{Style.RESET_ALL}")
        return
    
    user_id = user_results[0][0]
    
    update_query = "UPDATE TwoFactorAuth SET BackupCodes = ? WHERE UserID = ?"
    db.execute_query(update_query, params=(new_codes_str, user_id), fetch=False, autocommit=True)
    
    print(f"\n{Fore.GREEN}✓ New backup codes generated!{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}Your new backup codes:{Style.RESET_ALL}\n")
    for i, code in enumerate(new_codes, 1):
        print(f"  {i:2d}. {code}")
    
    print(f"\n{Fore.YELLOW}⚠ Save these codes in a safe place!{Style.RESET_ALL}")
    
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")


def test_2fa_code(db, username):
    """Test a 2FA code to verify it's working"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}TEST 2FA CODE{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    secret, _ = get_user_secret(db, username)
    
    if not secret:
        print(f"{Fore.RED}2FA is not properly configured!{Style.RESET_ALL}")
        return
    
    code = input(f"{Fore.CYAN}Enter 6-digit code from Google Authenticator: {Style.RESET_ALL}").strip()
    
    totp = pyotp.TOTP(secret)
    
    if totp.verify(code):
        print(f"\n{Fore.GREEN}✓ Code is valid! Your 2FA is working correctly.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}✗ Invalid code!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Make sure:{Style.RESET_ALL}")
        print("  1. Time on your phone is synchronized")
        print("  2. You're using the correct account in Google Authenticator")
        print("  3. Code hasn't expired (codes refresh every 30 seconds)")


def verify_2fa_login(db, username):
    """Verify 2FA code during login (called from main.py)"""
    if not check_2fa_status(db, username):
        return True  # 2FA not enabled, allow login
    
    secret, backup_codes_str = get_user_secret(db, username)
    
    if not secret:
        print(f"{Fore.RED}Error: 2FA configuration error!{Style.RESET_ALL}")
        return False
    
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}TWO-FACTOR AUTHENTICATION REQUIRED{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    for attempt in range(3):
        code = input(f"{Fore.CYAN}Enter 6-digit code from Google Authenticator: {Style.RESET_ALL}").strip()
        
        # Check TOTP code
        totp = pyotp.TOTP(secret)
        if totp.verify(code):
            print(f"{Fore.GREEN}✓ Code verified successfully!{Style.RESET_ALL}")
            return True
        
        # Check backup codes
        if backup_codes_str:
            backup_codes = backup_codes_str.split(',')
            if code in backup_codes:
                print(f"{Fore.GREEN}✓ Backup code accepted!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}This backup code has been used and will be removed.{Style.RESET_ALL}")
                
                # Remove used backup code
                backup_codes.remove(code)
                new_backup_codes_str = ','.join(backup_codes)
                
                user_id_query = "SELECT principal_id FROM sys.database_principals WHERE name = ?"
                columns, user_results = db.execute_query(user_id_query, params=(username,))
                
                if user_results:
                    user_id = user_results[0][0]
                    update_query = "UPDATE TwoFactorAuth SET BackupCodes = ? WHERE UserID = ?"
                    db.execute_query(update_query, params=(new_backup_codes_str, user_id), fetch=False, autocommit=True)
                
                return True
        
        print(f"{Fore.RED}✗ Invalid code! {2 - attempt} attempts remaining.{Style.RESET_ALL}")
    
    print(f"\n{Fore.RED}✗ Too many failed attempts. Access denied.{Style.RESET_ALL}")
    return False


def generate_backup_codes():
    """Generate 10 random backup codes"""
    import random
    import string
    
    codes = []
    for _ in range(10):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        formatted_code = f"{code[:4]}-{code[4:]}"
        codes.append(formatted_code)
    
    return codes


def show_2fa_info():
    """Show information about 2FA"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}ABOUT TWO-FACTOR AUTHENTICATION (2FA){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    print(f"{Fore.GREEN}What is 2FA?{Style.RESET_ALL}")
    print("Two-Factor Authentication adds an extra layer of security to your account.")
    print("Even if someone knows your password, they can't access your account without")
    print("the 6-digit code from your phone.\n")
    
    print(f"{Fore.GREEN}How it works:{Style.RESET_ALL}")
    print("1. You enable 2FA and scan a QR code with Google Authenticator app")
    print("2. The app generates a new 6-digit code every 30 seconds")
    print("3. When logging in, you enter your password + the current code\n")
    
    print(f"{Fore.GREEN}Compatible apps:{Style.RESET_ALL}")
    print("  • Google Authenticator (Android, iOS)")
    print("  • Microsoft Authenticator")
    print("  • Authy")
    print("  • FreeOTP\n")
    
    print(f"{Fore.GREEN}Backup codes:{Style.RESET_ALL}")
    print("When you enable 2FA, you'll receive 10 backup codes.")
    print("Keep them in a safe place - you can use them if you lose your phone.\n")
    
    print(f"{Fore.YELLOW}Download Google Authenticator:{Style.RESET_ALL}")
    print("  Android: https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2")
    print("  iOS: https://apps.apple.com/app/google-authenticator/id388497605")
    
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
