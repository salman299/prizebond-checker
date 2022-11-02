source venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)
python3 ./main.py
