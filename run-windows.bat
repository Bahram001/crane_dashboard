@echo off
REM Set up virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

REM Run the Streamlit app properly
streamlit run app\gui.py

pause
