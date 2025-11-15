# Avatar Platform (Simple Flask + HTML demo)

## Setup (local)
1. Create a Python virtual env:
   python -m venv venv
   source venv/bin/activate    # mac/linux
   venv\Scripts\activate       # windows

2. Install requirements:
   pip install -r requirements.txt

3. Run the app:
   python app.py
   # or FLASK_APP=app.py flask run

4. Open in browser:
   http://127.0.0.1:5000/

## Notes
- Default DB: sqlite file `avatar_platform.db` created automatically.
- The platform auto-seeds a few demo products the first time it runs.
- SECRET_KEY is set to a default for demo: set environment variable `SECRET_KEY` in production.
- To add real avatar features: replace the placeholder UI in `templates/product.html` with your TTS/AV pipeline calls to backend endpoints.
