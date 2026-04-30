import os
import re
import uuid
from pathlib import Path

from flask import (Flask, abort, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from sqlalchemy import func, or_
from werkzeug.utils import secure_filename

from models import Comment, Rating, Recipe, ThumbsUp, User, db

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / 'static' / 'uploads'
ALLOWED_IMAGE_EXTS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
USERNAME_RE = re.compile(r'^[A-Za-z0-9_.-]{2,80}$')
MIN_PASSWORD_LEN = 6


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', f'sqlite:///{BASE_DIR / "recipes.db"}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB uploads

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


# ---------- Helpers ----------

def current_user():
    if 'user_id' not in session:
        return None
    if getattr(g, '_current_user', None) is not None:
        return g._current_user
    user = db.session.get(User, session['user_id'])
    g._current_user = user
    return user


def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            flash('Please sign in to continue.', 'warning')
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)

    return wrapped


def allowed_image(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTS


def save_image(file_storage) -> str | None:
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_image(file_storage.filename):
        flash('Unsupported image type.', 'danger')
        return None
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    name = f'{uuid.uuid4().hex}.{ext}'
    safe = secure_filename(name)
    file_storage.save(UPLOAD_DIR / safe)
    return safe


# ---------- Routes ----------

def register_routes(app: Flask):

    @app.context_processor
    def inject_user():
        return {'current_user': current_user()}

    # Home: list + search/filter
    @app.route('/')
    def index():
        q = (request.args.get('q') or '').strip()
        tag = (request.args.get('tag') or '').strip()
        query = Recipe.query
        if q:
            like = f'%{q}%'
            query = query.filter(or_(
                Recipe.title.ilike(like),
                Recipe.ingredients.ilike(like),
                Recipe.description.ilike(like),
            ))
        if tag:
            query = query.filter(Recipe.tags.ilike(f'%{tag}%'))
        recipes = query.order_by(Recipe.created_at.desc()).all()
        return render_template('index.html', recipes=recipes, q=q, tag=tag)

    # --- Auth (open sign-up + password login) ---
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = (request.form.get('username') or '').strip().lower()
            password = request.form.get('password') or ''
            if not username or not password:
                flash('Username and password are required.', 'danger')
                return render_template('login.html', form=request.form)
            user = User.query.filter_by(username=username).first()
            if user is None or not user.check_password(password):
                flash('Invalid username or password.', 'danger')
                return render_template('login.html', form=request.form)
            session['user_id'] = user.id
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        return render_template('login.html', form={})

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = (request.form.get('username') or '').strip().lower()
            display_name = (request.form.get('display_name') or '').strip()
            password = request.form.get('password') or ''
            confirm = request.form.get('confirm_password') or ''
            errors = []
            if not USERNAME_RE.match(username):
                errors.append('Username must be 2-80 chars: letters, numbers, dot, dash, underscore.')
            elif User.query.filter_by(username=username).first():
                errors.append('That username is already taken.')
            if len(password) < MIN_PASSWORD_LEN:
                errors.append(f'Password must be at least {MIN_PASSWORD_LEN} characters.')
            if password != confirm:
                errors.append('Passwords do not match.')
            if errors:
                for e in errors:
                    flash(e, 'danger')
                return render_template('signup.html', form=request.form)
            user = User(username=username, display_name=display_name or None)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            flash(f'Welcome, {user.name}! Account created.', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        return render_template('signup.html', form={})

    @app.route('/logout', methods=['POST'])
    def logout():
        session.pop('user_id', None)
        flash('Signed out.', 'info')
        return redirect(url_for('index'))

    # --- Profile ---
    @app.route('/users/<username>')
    def profile(username):
        user = User.query.filter_by(username=username.lower()).first_or_404()
        return render_template('profile.html', user=user)

    @app.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        user = current_user()
        if request.method == 'POST':
            user.display_name = (request.form.get('display_name') or '').strip() or None
            user.bio = (request.form.get('bio') or '').strip() or None
            db.session.commit()
            flash('Profile updated.', 'success')
            return redirect(url_for('profile', username=user.username))
        return render_template('edit_profile.html', user=user)

    # --- Recipes ---
    @app.route('/recipes/new', methods=['GET', 'POST'])
    @login_required
    def new_recipe():
        if request.method == 'POST':
            title = (request.form.get('title') or '').strip()
            ingredients = (request.form.get('ingredients') or '').strip()
            instructions = (request.form.get('instructions') or '').strip()
            description = (request.form.get('description') or '').strip() or None
            tags = (request.form.get('tags') or '').strip() or None
            if not (title and ingredients and instructions):
                flash('Title, ingredients, and instructions are required.', 'danger')
                return render_template('new_recipe.html',
                                       form=request.form)
            image_filename = save_image(request.files.get('image'))
            recipe = Recipe(
                title=title, ingredients=ingredients, instructions=instructions,
                description=description, tags=tags, image_filename=image_filename,
                owner=current_user(),
            )
            db.session.add(recipe)
            db.session.commit()
            flash('Recipe added!', 'success')
            return redirect(url_for('recipe_detail', recipe_id=recipe.id))
        return render_template('new_recipe.html', form={})

    @app.route('/recipes/<int:recipe_id>')
    def recipe_detail(recipe_id):
        recipe = db.session.get(Recipe, recipe_id) or abort(404)
        user = current_user()
        user_thumbed = False
        user_rating = 0
        if user:
            user_thumbed = ThumbsUp.query.filter_by(
                recipe_id=recipe.id, user_id=user.id).first() is not None
            r = Rating.query.filter_by(recipe_id=recipe.id, user_id=user.id).first()
            user_rating = r.stars if r else 0
        return render_template('recipe.html', recipe=recipe,
                               user_thumbed=user_thumbed,
                               user_rating=user_rating)

    @app.route('/recipes/<int:recipe_id>/delete', methods=['POST'])
    @login_required
    def delete_recipe(recipe_id):
        recipe = db.session.get(Recipe, recipe_id) or abort(404)
        if recipe.owner_id != current_user().id:
            abort(403)
        db.session.delete(recipe)
        db.session.commit()
        flash('Recipe deleted.', 'info')
        return redirect(url_for('index'))

    # --- Comments ---
    @app.route('/recipes/<int:recipe_id>/comment', methods=['POST'])
    @login_required
    def add_comment(recipe_id):
        recipe = db.session.get(Recipe, recipe_id) or abort(404)
        content = (request.form.get('content') or '').strip()
        if not content:
            flash('Comment cannot be empty.', 'danger')
        else:
            db.session.add(Comment(content=content, recipe=recipe,
                                   author=current_user()))
            db.session.commit()
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))

    # --- Thumbs up (toggle, AJAX-friendly) ---
    @app.route('/recipes/<int:recipe_id>/thumbs_up', methods=['POST'])
    @login_required
    def toggle_thumbs(recipe_id):
        recipe = db.session.get(Recipe, recipe_id) or abort(404)
        user = current_user()
        existing = ThumbsUp.query.filter_by(
            recipe_id=recipe.id, user_id=user.id).first()
        if existing:
            db.session.delete(existing)
            active = False
        else:
            db.session.add(ThumbsUp(recipe_id=recipe.id, user_id=user.id))
            active = True
        db.session.commit()
        count = ThumbsUp.query.filter_by(recipe_id=recipe.id).count()
        if request.headers.get('X-Requested-With') == 'fetch':
            return jsonify({'active': active, 'count': count})
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))

    # --- Ratings ---
    @app.route('/recipes/<int:recipe_id>/rate', methods=['POST'])
    @login_required
    def rate_recipe(recipe_id):
        recipe = db.session.get(Recipe, recipe_id) or abort(404)
        try:
            stars = int(request.form.get('stars', 0))
        except ValueError:
            stars = 0
        if stars < 1 or stars > 5:
            if request.headers.get('X-Requested-With') == 'fetch':
                return jsonify({'error': 'stars must be 1..5'}), 400
            flash('Rating must be 1-5 stars.', 'danger')
            return redirect(url_for('recipe_detail', recipe_id=recipe.id))
        user = current_user()
        rating = Rating.query.filter_by(
            recipe_id=recipe.id, user_id=user.id).first()
        if rating:
            rating.stars = stars
        else:
            rating = Rating(recipe_id=recipe.id, user_id=user.id, stars=stars)
            db.session.add(rating)
        db.session.commit()

        avg = db.session.query(func.avg(Rating.stars)).filter(
            Rating.recipe_id == recipe.id).scalar() or 0
        if request.headers.get('X-Requested-With') == 'fetch':
            return jsonify({'stars': stars, 'average': round(float(avg), 1),
                            'count': len(recipe.ratings)})
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))

    @app.errorhandler(404)
    def not_found(_e):
        return render_template('error.html', code=404,
                               message='Page not found.'), 404

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template('error.html', code=403,
                               message='Not allowed.'), 403


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)