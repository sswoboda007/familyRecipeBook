from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    display_name = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    recipes = db.relationship('Recipe', backref='owner', lazy=True,
                              cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True,
                               cascade='all, delete-orphan')
    thumbs = db.relationship('ThumbsUp', backref='user', lazy=True,
                             cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='user', lazy=True,
                              cascade='all, delete-orphan')

    @property
    def name(self):
        return self.display_name or self.username


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=False)  # one ingredient per line
    instructions = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), nullable=True)   # comma-separated
    image_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comments = db.relationship('Comment', backref='recipe', lazy=True,
                               cascade='all, delete-orphan',
                               order_by='Comment.created_at.desc()')
    thumbs = db.relationship('ThumbsUp', backref='recipe', lazy=True,
                             cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='recipe', lazy=True,
                              cascade='all, delete-orphan')

    @property
    def ingredient_list(self):
        return [line.strip() for line in (self.ingredients or '').splitlines() if line.strip()]

    @property
    def tag_list(self):
        return [t.strip() for t in (self.tags or '').split(',') if t.strip()]

    @property
    def thumbs_count(self):
        return len(self.thumbs)

    @property
    def average_rating(self):
        if not self.ratings:
            return 0.0
        return round(sum(r.stars for r in self.ratings) / len(self.ratings), 1)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class ThumbsUp(db.Model):
    __tablename__ = 'thumbs_up'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('recipe_id', 'user_id', name='uq_thumbs_recipe_user'),
    )


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)  # 1..5
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('recipe_id', 'user_id', name='uq_rating_recipe_user'),
        db.CheckConstraint('stars >= 1 AND stars <= 5', name='ck_rating_stars_range'),
    )