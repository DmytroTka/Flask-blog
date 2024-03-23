from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from models import Post, User, db, PostLikes, PostDislikes
from flask_login import login_user, login_required, LoginManager, logout_user, UserMixin, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskoblog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        new_user = User(username=username, password=password)

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user, remember=True)

            return redirect(url_for('index'))
        else:
            flash('User is not found, check password and login.')
    return render_template('login.html')


@app.route('/')
@login_required
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/new', methods=['GET', "POST"])
@login_required
def new_post():
    # pass
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            post = Post(title=title, content=content)
            db.session.add(post)
            db.session.commit()
            flash('The post was successfully added!', 'success')
        else:
            flash('Post`s title and content fields must be filled!', 'danger')
    return render_template('new.html')


@app.route('/post/<int:id>')
@login_required
def post(id):
    # pass
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            post.title = title
            post.content = content
            db.session.add(post)
            db.session.commit()
            flash('The post was successfully edited!', 'success')
            return redirect(url_for('post', id=post.id))
        else:
            flash('A title and a content must be filled!', 'danger')

    return render_template('edit.html', post=post)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(post)
        db.session.commit()
        flash('The post was successfully deleted!')
        return redirect(url_for('index'))
    return render_template('delete.html', post=post)#


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


def create_table():
    db.create_all()


@app.route('/like_post/<int:id>', methods=['POST'])
@login_required
def like_post(id):
    post = Post.query.get_or_404(id)
    if current_user in post.liked_by:
        flash('You have already liked this post!', 'warning')
    else:
        post.likes += 1
        post.liked_by.append(current_user)
        if current_user in post.disliked_by:
            post.dislikes -= 1
            post.disliked_by.remove(current_user)
        db.session.commit()
    return redirect(url_for('post', id=post.id))


@app.route('/dislike_post/<int:id>', methods=['POST'])
@login_required
def dislike_post(id):
    post = Post.query.get_or_404(id)
    if current_user in post.disliked_by:
        flash('You have already liked this post!', 'warning')
    else:
        post.dislikes += 1
        post.disliked_by.append(current_user)
        if current_user in post.liked_by:
            post.likes -= 1
            post.liked_by.remove(current_user)
        db.session.commit()
    return redirect(url_for('post', id=post.id))


if __name__ == '__main__':
    with app.app_context():
        create_table()
    app.run(debug=True)
