import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSpreadsheetManager:
    def __init__(self, json_keyfile, spreadsheet_url):
        self.json_keyfile = json_keyfile
        self.spreadsheet_url = spreadsheet_url
        self.client = self.authenticate_gspread()
        self.spreadsheet = self.get_spreadsheet()

    def authenticate_gspread(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.json_keyfile, scope)
        return gspread.authorize(creds)

    def get_spreadsheet(self):
        return self.client.open_by_url(self.spreadsheet_url)

    def copy_sheet(self, source_sheet_name, new_sheet_name):
        source_sheet = self.spreadsheet.worksheet(source_sheet_name)
        source_sheet.duplicate(new_sheet_name=new_sheet_name, insert_sheet_index=1)

    def rename_sheet(self, old_name, new_name):
        sheet = self.spreadsheet.worksheet(old_name)
        sheet.update_title(new_name)

    def edit_cell(self, sheet_name, row, col, value):
        sheet = self.spreadsheet.worksheet(sheet_name)
        sheet.update_cell(row, col, value)

if __name__ == "__main__":
    JSON_KEYFILE = "client_secret.json"
    SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1NngcnXZGm_kWHHPRmA95seKWpKkF3pFmQT0XFGtp02k/edit?usp=drive_link"
    
    manager = GoogleSpreadsheetManager(JSON_KEYFILE, SPREADSHEET_URL)
    
    manager.copy_sheet("SourceSheet", "NewSheet")
    manager.rename_sheet("OldSheetName", "NewSheetName")
    manager.edit_cell("SheetName", 1, 1, "New Value")