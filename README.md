[![Django CI](../../actions/workflows/unit-tests.yml/badge.svg)](../../actions/workflows/unit-tests.yml)

An application to conduct online polls and surveys based
on the [Django Tutorial project](https://docs.djangoproject.com/en/5.1/intro/tutorial01/), with
additional features.

The project will produce a web application for conducting polls and surveys that satisfies the requirements as specified in [Requirements](https://github.com/KikyoBRV/ku-polls/wiki/Requirements). The application will be written in Python and runnable on Windows, Linux, or MacOS hosts containing the required software.

## Requirements
* Requires Python 3.10+ or newer. Required Python packages are listed in [requirements.txt](https://github.com/KikyoBRV/ku-polls/blob/main/requirements.txt).

## Installation and configuration
You can see the step in [Installation and configuration](../../wiki/Installation-and-configuration)

## Running the Application
1. Activate the virtual environment
   * On Linux or MacOS
   ```
   source venv/bin/activate
   ```
   * On Window
   ```
   venv\Scripts\activate
   ```
2. Start the Django development server
   ```
   python manage.py runserver
   ```
3. Open the web browser and go to this URL
   ```
   http://127.0.0.1:8000/polls/
   ```
   If you want to deactivate the server, press `Ctrl + C`
4. To deactivate virtual environment
   ```
   deactivate
   ```

## Demo Admin Account
| Username | Password  |
|----------|-----------|
| admin    | iloveisp |

## Demo User Accounts
| Username | Password |
|----------|----------|
| demo1    | hackme11 |
| demo2    | hackme22 |
| demo3    | hackme33 |

## Project Documentation
All project documents are in the [Project Wiki](../../wiki/Home).
* [Vision and Scope](../../wiki/Vision-and-Scope)
* [Requirements](../../wiki/Requirements)
* [Project Plan](../../wiki/Project-Plan)

## Iteration Plans
* [Iteration 1 Plan](../../wiki/Iteration-1-Plan) 
* [Iteration 2 Plan](../../wiki/Iteration-2-Plan)
* [Iteration 3 Plan](../../wiki/Iteration-3-Plan) 