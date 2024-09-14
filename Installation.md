## Installation and configuration

1. Clone the repository
```
git clone https://github.com/KikyoBRV/ku-polls.git
```
2. Change directory to ku-polls
```
cd ku-polls
```
3. Create virtual environment
```
python -m venv venv
```
4. Activate virtual environment
    On MacOS or Linux:
    ```
    . venv/bin/activate
    ```
    On Windows:
    ```
    venv\Scripts\activate
    ```
5. Install required packages
```
pip install -r requirements.txt
```
6. Set Up the Secret Key (For Development) -- Create a file named .env in the same directory as "manage.py"
```
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```
On Linux/MacOS:
```
cp sample.env .env
```
On Windows:
```
copy sample.env .env
```
7. Run database migration
```
python manage.py migrate
```
8. Load initial data
```
python manage.py loaddata data/users.json
```
```
python manage.py loaddata data/polls-v4.json
```
9. Run server
```
python manage.py runserver
```
note: if css not show try to use
```
python manage.py runserver --insecure
```


