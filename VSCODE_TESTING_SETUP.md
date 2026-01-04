# VS Code Testing Setup Guide

## Issue
VS Code is using the system Python interpreter instead of the virtual environment.

## Solution

### Step 1: Open the Correct Workspace Folder
1. In VS Code, go to **File > Open Folder**
2. Navigate to and open: `C:\Users\sidda\Documents\projects\basic-stock-eda`
3. **Important**: Open the `basic-stock-eda` folder directly, NOT the parent `projects` folder

### Step 2: Select the Virtual Environment Python Interpreter
1. Press `Ctrl+Shift+P` to open the Command Palette
2. Type: `Python: Select Interpreter`
3. Select the interpreter that shows: `.\.venv\Scripts\python.exe` (Python 3.14.2)
   - It should show something like: `Python 3.14.2 64-bit ('.venv': venv)`

### Step 3: Refresh Test Discovery
1. Open the **Testing** view (click the beaker icon in the left sidebar, or press `Ctrl+Shift+T`)
2. Click the **Refresh Tests** button (circular arrow icon at the top)
3. You should now see all 70 tests organized by file:
   - test_base.py (7 tests)
   - test_buy_once.py (11 tests)
   - test_dca_friday.py (12 tests)
   - test_earnings_play.py (13 tests)
   - test_intraday.py (13 tests)
   - test_intraday_hold_profit.py (14 tests)

### Step 4: Run Tests from VS Code GUI
- Click the **Run All Tests** button (double play icon) to run all tests
- Click individual test files or test cases to run them separately
- Click the green checkmark to see test details
- Failed tests will show a red X (all should be green!)

## Troubleshooting

### If tests still don't appear:
1. Make sure pytest is installed in the virtual environment:
   ```powershell
   .venv\Scripts\python.exe -m pip install pytest
   ```

2. Reload VS Code window:
   - Press `Ctrl+Shift+P`
   - Type: `Developer: Reload Window`

3. Check the OUTPUT panel:
   - View > Output
   - Select "Python Test Log" from the dropdown
   - Look for any error messages

### If wrong Python interpreter is selected:
1. Check bottom-left status bar - it should show: `Python 3.14.2 64-bit ('.venv': venv)`
2. If it shows a different version, click it and select the `.venv` interpreter

### Verify Configuration:
The `.vscode/settings.json` file has been created with the correct settings:
- Python testing enabled with pytest
- Default interpreter set to `.venv/Scripts/python.exe`
- Test root directory set to `tests/`

## Expected Result
After following these steps, you should see:
- ✅ 70 tests discovered in the Testing view
- ✅ All tests passing (green checkmarks)
- ✅ Ability to run individual tests by clicking them
- ✅ Test output showing in the terminal when tests run
