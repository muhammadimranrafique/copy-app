from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import List, Dict, Any
from config import get_settings
import os

settings = get_settings()

class GoogleSheetsService:
    def __init__(self):
        self.sheet_id = settings.google_sheet_id
        self.credentials_path = settings.google_credentials_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API using service account credentials."""
        if not os.path.exists(self.credentials_path):
            print(f"Warning: Credentials file not found at {self.credentials_path}")
            return
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
        except Exception as e:
            print(f"Error authenticating with Google Sheets: {e}")
    
    def append_row(self, sheet_name: str, values: List[Any]):
        """Append a row to the specified sheet."""
        if not self.service:
            print("Google Sheets service not available")
            return False
        
        try:
            body = {'values': [values]}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=f'{sheet_name}!A:Z',
                valueInputOption='RAW',
                body=body
            ).execute()
            return True
        except Exception as e:
            print(f"Error appending row to Google Sheets: {e}")
            return False
    
    def update_row(self, sheet_name: str, row_index: int, values: List[Any]):
        """Update a row in the specified sheet."""
        if not self.service:
            print("Google Sheets service not available")
            return False
        
        try:
            body = {'values': [values]}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=f'{sheet_name}!A{row_index}:Z{row_index}',
                valueInputOption='RAW',
                body=body
            ).execute()
            return True
        except Exception as e:
            print(f"Error updating row in Google Sheets: {e}")
            return False
    
    def get_all_rows(self, sheet_name: str) -> List[List[Any]]:
        """Get all rows from the specified sheet."""
        if not self.service:
            print("Google Sheets service not available")
            return []
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f'{sheet_name}!A:Z'
            ).execute()
            return result.get('values', [])
        except Exception as e:
            print(f"Error getting rows from Google Sheets: {e}")
            return []
    
    def sync_client(self, client_data: Dict[str, Any]):
        """Sync client data to Google Sheets."""
        values = [
            str(client_data.get('id', '')),
            client_data.get('name', ''),
            client_data.get('type', ''),
            client_data.get('contact', ''),
            client_data.get('address', ''),
            client_data.get('opening_balance', 0),
            str(client_data.get('created_at', ''))
        ]
        return self.append_row('Clients', values)
    
    def sync_order(self, order_data: Dict[str, Any]):
        """Sync order data to Google Sheets."""
        values = [
            str(order_data.get('id', '')),
            order_data.get('order_number', ''),
            str(order_data.get('client_id', '')),
            str(order_data.get('order_date', '')),
            order_data.get('total_amount', 0),
            order_data.get('status', ''),
            str(order_data.get('created_at', ''))
        ]
        return self.append_row('Orders', values)
    
    def sync_payment(self, payment_data: Dict[str, Any]):
        """Sync payment data to Google Sheets."""
        values = [
            str(payment_data.get('id', '')),
            str(payment_data.get('order_id', '')),
            payment_data.get('amount', 0),
            payment_data.get('mode', ''),
            payment_data.get('status', ''),
            payment_data.get('reference_number', ''),
            str(payment_data.get('payment_date', '')),
            str(payment_data.get('created_at', ''))
        ]
        return self.append_row('Payments', values)
    
    def sync_expense(self, expense_data: Dict[str, Any]):
        """Sync expense data to Google Sheets."""
        values = [
            str(expense_data.get('id', '')),
            expense_data.get('category', ''),
            expense_data.get('amount', 0),
            expense_data.get('description', ''),
            str(expense_data.get('expense_date', '')),
            str(expense_data.get('created_at', ''))
        ]
        return self.append_row('Expenses', values)
    
    def sync_product(self, product_data: Dict[str, Any]):
        """Sync product data to Google Sheets."""
        values = [
            str(product_data.get('id', '')),
            product_data.get('name', ''),
            product_data.get('category', ''),
            product_data.get('cost_price', 0),
            product_data.get('sale_price', 0),
            product_data.get('stock_quantity', 0),
            product_data.get('unit', ''),
            str(product_data.get('created_at', '')),
            str(product_data.get('updated_at', ''))
        ]
        return self.append_row('Products', values)

# Global instance
sheets_service = GoogleSheetsService()

