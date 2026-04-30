# family recipe book

## Problem
I want all to be able to comment on each others recipes, give thumbs up.

## Users
- family

## Features
- users to have their own profiles
- upload recipes
- upload photos
- comment on recipes
- give thumbs up
- searching/filtering for recipes
- rating recipes with stars

## Tech Stack
- **language**: Python
- **framework**: Flask

## File Tree
- `app.py` - Main application file that initializes the Flask app and routes for the recipe book.
- `models.py` - Defines the data models for recipes, users, and comments using SQLAlchemy.
- `templates/index.html` - Homepage template displaying recipes and a search bar for filtering.
- `templates/recipe.html` - Template for displaying individual recipes and comments section.
- `static/style.css` - CSS file for styling the application.
- `static/scripts.js` - JavaScript file for handling user interactions such as thumbs up and comments.
- `requirements.txt` - List of Python dependencies required for the project, such as Flask and SQLAlchemy.
- `README.md` - Documentation file explaining how to set up and run the recipe book application.
