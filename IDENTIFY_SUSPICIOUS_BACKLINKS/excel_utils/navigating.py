"""
Navigation utilities for Excel workbooks.
"""

from openpyxl.worksheet.hyperlink import Hyperlink
from openpyxl.styles import Font, Color

def add_navigation_links(worksheet_or_workbook, target_sheet_name, row, column):
    """
    Add navigation links to a worksheet.
    
    Args:
        worksheet_or_workbook: The worksheet to add links to, or workbook if target_sheet is provided
        target_sheet_name: The name of the sheet to link to
        row: The row number to add the link
        column: The column number to add the link
    """
    # If a workbook is passed, get the active sheet
    if hasattr(worksheet_or_workbook, 'active'):
        worksheet = worksheet_or_workbook.active
    else:
        worksheet = worksheet_or_workbook
        
    cell = worksheet.cell(row=row, column=column)
    cell.hyperlink = Hyperlink(ref=f"'{target_sheet_name}'!A1", display=target_sheet_name)
    cell.font = Font(color=Color(rgb="0000FF"), underline="single")
    cell.value = target_sheet_name

def add_navigation_between_dodgy_sheets(workbook, sheet_names):
    """
    Add navigation links between dodgy sheets.
    
    Args:
        workbook: The workbook containing the sheets
        sheet_names: List of sheet names to link between
    """
    for i, sheet_name in enumerate(sheet_names):
        worksheet = workbook[sheet_name]
        if i > 0:
            add_navigation_links(worksheet, sheet_names[i-1], 1, 1)
        if i < len(sheet_names) - 1:
            add_navigation_links(worksheet, sheet_names[i+1], 1, 2) 