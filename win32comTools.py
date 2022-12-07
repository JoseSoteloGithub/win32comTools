import sys
import win32com.client
import win32api

constants = win32com.client.constants


class TableInWorksheet:
    def __init__(
        self, worksheet: object, header_row: int, starting_column: int
    ) -> None:
        self.worksheet: object = worksheet
        self.header_row: int = header_row
        self.starting_column: int = starting_column
        self.get_last_column()
        self.get_last_row()
        self.get_table_range()
        self.get_table_dict_li()
        super().__init__()

    def get_last_column(self):
        self.last_column = get_last_column_index(self.worksheet, self.header_row)
        return self.last_column

    def get_last_row(self):
        self.last_row = get_last_row(self.worksheet)
        return self.last_row

    def get_table_range(self):
        self.table_range = get_range_from_int_args(
            target_ws=self.worksheet,
            start_row=self.header_row,
            start_column=self.starting_column,
            end_row=self.last_row,
            end_column=self.last_column,
        )
        return self.table_range

    def get_table_dict_li(self):
        self.table_dict_li = get_dict_li_from_range(self.table_range)


def handle_type_error_com_can_not_automate_makepy(type_error_str):

    response = win32api.MessageBox(
        0, "Currently selected in a cell in Excel, click off and retry", "Complete"
    )

    sys.exit()


def handle_attribute_error_CLSIDToClassMap(attribute_error_str):
    # Use this on Attribute Error "has no attribute 'CLSIDToClassMap'"
    # This error happens when on this call win32com.client.Dispatch()
    from shutil import rmtree

    first_section_find_str = "win32com.gen_py."
    first_section_index = attribute_error_str.find(first_section_find_str)
    first_section_index += len(first_section_find_str)
    second_section_index = attribute_error_str.find("'", first_section_index)
    folder_name = attribute_error_str[first_section_index:second_section_index]
    rmtree(f"{win32com.__gen_path__}\{folder_name}")
    sys.exit(
        f"AttributeError detected and path {win32com.__gen_path__}\{folder_name} has been removed.  Restart the program"
    )


def get_range_whole(findString, currentSheet, withinRange=None, afterRange=None):

    if len(findString) <= 255:

        if (withinRange is None) and (afterRange is None):
            getPosition = currentSheet.Cells.Find(
                What=findString,
                After=currentSheet.Range("A1"),
                LookAt=constants.xlWhole,
                SearchDirection=constants.xlNext,
            )

        if (not withinRange is None) and (afterRange is None):
            getPosition = currentSheet.Range(withinRange.Address).Find(
                What=findString,
                After=currentSheet.Range("A" + withinRange.Row),
                LookAt=constants.xlWhole,
                SearchDirection=constants.xlNext,
            )

        elif (not withinRange is None) and (not afterRange is None):
            getPosition = currentSheet.Range(withinRange.Address).Find(
                What=findString,
                After=currentSheet.Range(afterRange.Address),
                LookAt=constants.xlWhole,
                SearchDirection=constants.xlNext,
            )

        elif (withinRange is None) and (not afterRange is None):
            getPosition = currentSheet.Cells.Find(
                What=findString,
                After=currentSheet.Range(afterRange.Address),
                LookAt=constants.xlWhole,
                SearchDirection=constants.xlNext,
            )

    get_range_whole = getPosition

    return get_range_whole


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


def get_column_letter(
    worksheet_obj, substring_str, header_row_int, worksheet_column_letters_dict={}
):
    # Returns column letter or -1 if not found
    try:
        column_letter = worksheet_column_letters_dict[substring_str]
        print("Returned from try: on worksheet_column_letters_dict")
        return column_letter
    except:
        if header_row_int == 0:
            column_header = worksheet_obj.Cells.Find(
                What=substring_str,
                SearchOrder=constants.xlByRows,
                SearchDirection=constants.xlNext,
                LookAt=constants.xlWhole,
            )
        else:
            column_header = worksheet_obj.Rows(header_row_int).Find(
                What=substring_str,
                SearchOrder=constants.xlByRows,
                SearchDirection=constants.xlNext,
                LookAt=constants.xlWhole,
            )

        if not column_header is None:
            first_dolla = find_nth(column_header.Address, "$", 1)
            second_dolla = find_nth(column_header.Address, "$", 2)
            column_letter = column_header.Address[first_dolla + 1 : second_dolla]
        else:
            column_letter = -1

        return column_letter


def get_column_number(
    worksheet_obj, substring_str, header_row_int, worksheet_column_numbers_dict={}
):
    # Returns column number or -1 if not found
    try:
        column_number = worksheet_column_numbers_dict[substring_str]
        print("Returned from try: on worksheet_column_numbers_dict")
        return column_number
    except:
        if header_row_int == 0:
            column_header = worksheet_obj.Cells.Find(
                What=substring_str,
                SearchOrder=constants.xlByRows,
                SearchDirection=constants.xlNext,
                LookAt=constants.xlWhole,
            )
        else:
            column_header = worksheet_obj.Rows(header_row_int).Find(
                What=substring_str,
                SearchOrder=constants.xlByRows,
                SearchDirection=constants.xlNext,
                LookAt=constants.xlWhole,
            )

        if not column_header is None:
            column_number = column_header.Column
        else:
            column_number = -1

        return column_number


def get_last_column_range(worksheet_obj: object, header_row_int=0):
    if header_row_int > 0:
        last_column_range = worksheet_obj.Rows(header_row_int).Find(
            What="*",
            SearchOrder=constants.xlByColumns,
            SearchDirection=constants.xlPrevious,
        )
    else:
        last_column_range = worksheet_obj.Cells.Find(
            What="*",
            SearchOrder=constants.xlByColumns,
            SearchDirection=constants.xlPrevious,
        )
    while last_column_range.Offset(1, 2).Value is not None:
        last_column_range = last_column_range.Offset(1, 2)

    return last_column_range


def get_last_column_letter(worksheet_obj: object, header_row_int=0) -> str:
    # Returns last column letter

    last_column_range = get_last_column_range(worksheet_obj, header_row_int)

    if last_column_range.Value is None:
        last_column_letter = None
    else:
        last_column_letter = last_column_range.Address.split("$")[1]

    return last_column_letter


def get_last_column_index(worksheet_obj: object, header_row_int=0) -> int:
    # Returns last column as index

    last_column_range = get_last_column_range(worksheet_obj, header_row_int)

    if last_column_range.Value is None:
        return 0
    else:
        return last_column_range.Column


def get_header_row(worksheet_obj, search_string_str):
    # returns header row as int, -1 if not found
    header_range = worksheet_obj.Rows.Find(
        What=search_string_str,
        LookAt=constants.xlWhole,
        SearchOrder=constants.xlByRows,
        SearchDirection=constants.xlNext,
    )
    if not header_range is None:
        header_row = header_range.Row
    else:
        header_row = -1
    return header_row


def get_last_row(worksheet_obj):
    # Returns last row as int
    last_row_range = worksheet_obj.Cells.Find(
        What="*", SearchOrder=constants.xlByRows, SearchDirection=constants.xlPrevious
    )

    if last_row_range is None:
        last_row = 1
    else:
        last_row = last_row_range.Row

    return last_row


def sheet_exist(workbook, string):
    # Returns True if exists
    for ws_target in workbook.Worksheets:
        if string in ws_target.Name:
            return True
    return False


def create_sheets(workbook_obj, worksheet_obj, name_li):
    # Loop through list of name, check if there's a worksheet for the name,
    # if not then copy the Active worksheet and paste it at the end, rename it, apply filter for that name
    for name in name_li:
        name_sheet_exist = sheet_exist(workbook_obj, name)
        if name_sheet_exist == False:
            worksheet_obj.Copy(After=workbook_obj.Sheets(len(workbook_obj.Worksheets)))
            workbook_obj.Worksheets(len(workbook_obj.Worksheets)).Name = name


def get_dictionary_column_letters(worksheet_obj, column_letters_dict, header_row_int):
    # Return dictionary of column letters dictionary_name['ColumnHeaderString'] = 'ColumnLetter'

    last_column_index = get_last_column_index(worksheet_obj, header_row_int)

    for i in range(1, last_column_index + 1):
        value = worksheet_obj.Range(
            worksheet_obj.Cells(header_row_int, i),
            worksheet_obj.Cells(header_row_int, i),
        ).Value
        column_letters_dict[value] = get_column_letter(
            worksheet_obj, value, header_row_int, column_letters_dict
        )

    return column_letters_dict


def get_dictionary_column_indices(worksheet_obj, column_indices_dict, header_row_int):
    # Return dictionary of column numbers dictionary_name['ColumnHeaderString'] = 'ColumnLetter'
    last_column_index = get_last_column_index(worksheet_obj, header_row_int)

    for i in range(1, last_column_index + 1):
        value = worksheet_obj.Range(
            worksheet_obj.Cells(header_row_int, i),
            worksheet_obj.Cells(header_row_int, i),
        ).Value
        column_indices_dict[value] = get_column_number(
            worksheet_obj, value, header_row_int, column_indices_dict
        )

    return column_indices_dict


def show_all_data_from_sheet(ws: object) -> None:
    # Shows all data in worksheet, unhides columns and rows, then clears filter
    ws.Cells.EntireRow.Hidden = False

    ws.Cells.EntireColumn.Hidden = False

    if (ws.AutoFilterMode and ws.FilterMode) or ws.FilterMode:
        ws.ShowAllData()

    return None


def get_wb_name_w_o_extension(filename: str) -> str:
    # Returns the file name without the extension
    wb_w_o_extension_period_index: int = find_nth(filename, ".", -1)
    wb_w_o_extension: str = filename[:wb_w_o_extension_period_index]
    return wb_w_o_extension


def get_filename_from_full_filename(full_filename: str) -> str:
    # Returns the file name from a path
    last_backslash_index: int = full_filename.rfind("\\")
    return full_filename[last_backslash_index + 1 :]


def get_open_workbook(wb_name_w_o_extension: str, excel_session: object) -> object:
    # Returns a workbook object or None if a workbook is not named the same as argument wb_name_w_o_extension
    target_wb: object
    for target_wb in excel_session.Workbooks:
        target_wb_name: str = target_wb.Name
        target_wb_w_o_extension_period_index: int = find_nth(target_wb_name, ".", -1)
        target_wb_w_o_extension: str = target_wb_name[
            :target_wb_w_o_extension_period_index
        ]
        if target_wb_w_o_extension.upper() == wb_name_w_o_extension.upper():
            return target_wb
    return None


def get_open_workbook_or_open_it(wb_full_filename: str, excel_session: object) -> object:
    # Returns a workbook object or None if the workbook is not open or not in the provided path
    wb_filename: str = get_filename_from_full_filename(wb_full_filename)
    wb_name_w_o_extension: str = get_wb_name_w_o_extension(wb_filename)
    wb: object = get_open_workbook(wb_name_w_o_extension, excel_session)
    if wb is None:
        wb: object = excel_session.Workbooks.Open(wb_full_filename)
    if wb is None:
        win32api.MessageBox(
            0,
            f"{wb_name_w_o_extension} workbook was not found at {wb_full_filename}.  Exiting",
            "Workbook not found",
        )
        return None
    return wb


def get_dict_li_from_range(target_range: object) -> dict:
    # Returns a list of dictionaries made of strings where the Key is the column and the Values are the values from the cells
    # Returns a strings only to avoid the complexity of dates
    # target_range is an Excel range object, target_range examples...
    # Example0: target_range = thisworksheet.Range("A1:Z27")
    # Example1: target_range = thisworksheet.Range(thisworksheet.Cells(1, 1), thisworksheet.Cells(this_last_row, this_last_column_index))
    table_value: tuple = target_range.Value

    table_dict_li: list = []

    table_key_li: list = list(table_value[0])

    import pywintypes
    import datetime

    for i in range(1, len(table_value)):
        this_dict: dict = {}

        for i_key, key in enumerate(table_key_li):
            element: object = table_value[i][i_key]
            this_dict[key]: str = str(element)

        table_dict_li.append(this_dict)

    return table_dict_li


def get_range_from_int_args(
    target_ws: object, start_row: int, start_column: int, end_row: int, end_column: int
) -> object:
    # Returns a Range object, simplifies having to type the target_ws 3X
    return target_ws.Range(
        target_ws.Cells(start_row, start_column), target_ws.Cells(end_row, end_column)
    )


def ws_to_json(workbook: object, ws_dict: dict) -> None:
    # Required arguments in ws_dict, 'ws_name', 'ws_header_row', 'ws_header_column'
    # ws_dict['ws_name']
    # ws_dict['ws_header_row']
    # ws_dict['ws_header_column']
    ws: object = workbook.Worksheets(ws_dict["ws_name"])

    last_column_index: int = get_last_column_index(ws, ws_dict["ws_header_row"])

    last_row: int = get_last_row(ws)

    target_range: object = get_range_from_int_args(
        ws,
        ws_dict["ws_header_row"],
        ws_dict["ws_header_column"],
        last_row,
        last_column_index,
    )

    dict_li: list = get_dict_li_from_range(target_range)

    save_list_of_dict_as_json(dict_li, ws_dict["ws_name"])

    return None


def get_excel_session() -> object:
    try:
        # Attach to existing Excel session if available
        excel_session = win32com.client.GetActiveObject("Excel.Application")
    except Exception as exception:
        if "Operation unavailable" in str(exception):
            excel_session: object = win32com.client.Dispatch("Excel.Application")
    return excel_session

def get_excel_turbo_mode(excel_session: object, engaged_bool: bool) -> object:
    if engaged_bool:
        excel_session.ScreenUpdating = False

        excel_session.Calculation = constants.xlCalculationManual

        return None

    excel_session.ScreenUpdating = True

    excel_session.Calculation = constants.xlCalculationAutomatic     

    return None   

# This is more of a JSON thing than an excel thing
def save_list_of_dict_as_json(li: list, save_name: str) -> None:
    # Saves list of dictionaries as text file
    import json

    with open(f"{save_name}.json", "w") as convert_file:
        convert_file.write(json.dumps(li))
    return None


# Not directly related, dynamic operations
def dynamic_operator(a, relate_operator: str, b) -> bool:
    # Compares a to b with relate_operator as what it needs to check, returns True or False
    # https://docs.python.org/2/library/operator.html
    import operator

    def get_truth(inp, relate, cut):
        ops = {
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
        }
        return ops[relate](inp, cut)

    return get_truth(a, relate_operator, b)


def get_bool_if_dict_passes_conditions(target_dict: dict, conditions_dict_li: list) -> bool:
    # Returns true if target_dict passes the conditions tests
    """ conditions_dict_li = [
            {
                "condition_key": "Status",
                "condition_operator": "==",
                "condition_compare": "Open"
            },
            {
                "condition_key": "Date",
                "condition_operator": "==",
                "condition_compare": "None"
            }            
        ] """
    for condition in conditions_dict_li:
        this_result: bool = dynamic_operator(
            target_dict[condition["condition_key"]],
            condition["condition_operator"],
            condition["condition_compare"],
        )
        if not this_result:

            return False
            
    return True


def get_dict_li_from_config(target_dict_li: list, conditions_dict_li: list, return_keys: list) -> list:
    # COMBO of get_dict_list_from_conditions and get_return_keys_from_dict_li
    # Returns list of only return_keys and only values that met conditions_dict_li on target_dict_li
    dict_list_from_conditions: list = get_dict_list_from_conditions(target_dict_li, conditions_dict_li)

    return get_return_keys_from_dict_li(dict_list_from_conditions, return_keys)


# Not directly related,
def get_dict_list_from_conditions(target_dict_li: list, conditions_dict_li: dict) -> list:
    # Returns list of dictionaries based on the conditions provided
    """conditions_dict_li = [
                {
                    "condition_key": "Status",
                    "condition_operator": "==",
                    "condition_compare": "Open"
                }
            ]"""

    return_list: list = []
    for target_dict in target_dict_li:
        add_this_dict: bool = False

        add_this_dict = get_bool_if_dict_passes_conditions(target_dict, conditions_dict_li)

        if add_this_dict:
            
            return_list.append(target_dict)

    return return_list

def get_return_keys_from_dict_li(target_dict_li: list, return_keys: list) -> list:
    # Returns list of dictionaries made of only key values found in the return_keys list
    return_list: list = []
    for element in target_dict_li:
        return_dict: dict = {}
        for key in return_keys:
            return_dict[key] = element[key]
        return_list.append(return_dict)
    
    return return_list

def get_dict_li_from_key_relation(relation_destination_to_target_dict: dict, target_dict_li: list) -> None:
    # returns list of dictionaries made of new keys, destination_key1 will be the new key for the value in the target dict
    ''' relation_destination_to_target_dict = {
            "destination_key1": "target_key1",
            "destination_key2": "target_key2"
        }'''
    return_list = []
    for target_dict in target_dict_li:
        return_dict: dict = {}
        for element in relation_destination_to_target_dict:
            return_dict[element] = target_dict[relation_destination_to_target_dict[element]]
        return_list.append(return_dict)

    return return_list
