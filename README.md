# Family Recipe Book

## Overview
The Family Recipe Book is a collaborative platform designed for families to share and engage with each other's recipes. Users can comment on recipes, provide feedback through thumbs up, and have personalized profiles to manage their recipe contributions.

## Features
- **Open Sign-Up:** Anyone can create an account with a username and password — no invite required.
- **User Profiles:** Each member has their own profile with display name and bio.
- **Public Browsing:** Recipes can be viewed without an account. Posting, commenting, rating, and thumbs-up require sign-in.
- **Recipe Uploading:** Signed-in users can upload their own recipes along with photos.
- **Comments:** Signed-in users can comment on each other's recipes.
- **Thumbs Up:** Users can give thumbs up to show appreciation for recipes.
- **Search & Filter:** Recipes can be searched and filtered based on ingredients or dietary preferences.
- **Rating System:** Users can rate recipes using a star system.

## Accounts
- Visit `/signup` to create an account. Pick any available username (2-80 chars: letters, numbers, dot, dash, underscore) and a password of at least 6 characters.
- Visit `/login` to sign in. Authentication is required for any action that creates or modifies content.
- Logout from the nav header. Sessions are signed with `SECRET_KEY` (set this in production).

## Tech Stack
- **Language:** Python
- **Framework:** Flask

## Getting Started
To set up and run the Family Recipe Book application, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd family-recipe-book
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   flask run
   ```

5. **Access the application:**
   Open your web browser and go to `http://127.0.0.1:5000`.

6. **Create your first account:**
   Click **Sign up** in the header (or visit `/signup`) to register your username and password. You'll be signed in automatically.

### Environment Variables
- `SECRET_KEY` — used to sign session cookies. **Set a strong value in production.** Defaults to a development placeholder.
- `DATABASE_URL` — SQLAlchemy URI. Defaults to a local SQLite file at `recipes.db`.

### Resetting the Database (development)
The schema added a required `password_hash` column to existing user records. If you have an old `recipes.db` from a previous version, delete it before first run; the app will recreate the database with the new schema on startup.

## Ideas for Future Development
- **Recipe Search and Filter:** Allow users to more effectively find recipes based on specific criteria.
- **Recipe Rating System:** Implement a star system for detailed feedback on recipes.
- **Nutritional Information:** Include detailed nutritional facts for each recipe.

## Contributing
Contributions are welcome! Please feel free to submit issues or pull requests. 

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.