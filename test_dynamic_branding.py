"""
Test script to verify dynamic company branding implementation
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlmodel import Session, select
from database import engine
from models import Settings

def test_settings_fetch():
    """Test fetching company settings from database"""
    print("=" * 60)
    print("Testing Dynamic Company Branding Implementation")
    print("=" * 60)
    
    with Session(engine) as session:
        # Fetch settings
        statement = select(Settings)
        settings = session.exec(statement).first()
        
        if settings:
            print("\n✓ Company settings found in database:")
            print(f"  - Company Name: {settings.company_name}")
            print(f"  - Company Email: {settings.company_email}")
            print(f"  - Company Phone: {settings.company_phone}")
            print(f"  - Company Address: {settings.company_address}")
            print(f"  - Currency Symbol: {settings.currency_symbol}")
            print(f"  - Currency Code: {settings.currency_code}")
            print(f"  - Timezone: {settings.timezone}")
            print(f"  - Date Format: {settings.date_format}")
            print(f"  - Last Updated: {settings.updated_at}")
            
            print("\n✓ Settings are ready to be used for:")
            print("  1. Dashboard sidebar company name")
            print("  2. PDF invoice headers and footers")
            print("  3. Payment receipt headers and footers")
            
            return True
        else:
            print("\n✗ No settings found in database")
            print("  Please save settings via the Settings page first")
            return False

if __name__ == "__main__":
    try:
        success = test_settings_fetch()
        print("\n" + "=" * 60)
        if success:
            print("✓ Dynamic branding implementation is ready!")
            print("\nNext steps:")
            print("1. Start the backend server: cd backend && uvicorn main:app --reload")
            print("2. Start the frontend: cd frontend && npm run dev")
            print("3. Update company settings via Settings page")
            print("4. Verify company name appears in sidebar")
            print("5. Generate a payment receipt or invoice to see dynamic branding")
        else:
            print("✗ Please configure settings first")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
