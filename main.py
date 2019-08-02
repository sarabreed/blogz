from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'

#mysql+pymysql://username:password@port/database


app.config['SQLALCHEMY_ECHO'] = True
#this lets you see the sql from behind the scenes

db = SQLAlchemy(app)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

# TO DO: Add a User class to make all this new 

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')
    
# this initializer is what allows us to use dot notation
    def __init__(self, username, password):
        self.username = username
        self.password = password


#creating a persistent class that can be put in the database.
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#look at flick-list as well
#these are the values that you use to (dot notation) to link the tables
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

# this will run for every request
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blogs', 'index','post']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect ('/login')

#display the login page
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Yikes! This username does not exist.", 'error')
            return redirect ('/login') 

        if user and user.password == password:
            #remembers that the user has logged in
            session['username'] = username
            flash("You are Logged In.  Welcome back, "+user.username)
            return redirect ('/newpost')   
        elif user.password != password:
            flash("Whoopsies! That password is incorrect. Try again.", 'error') #  explain why the login failed
            return redirect ('/login')       
        
    return render_template('login.html')

#displa signup and validate signup data
@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form ['verify']
        existing_user = User.query.filter_by(username=username).first()
        errors = False  

        if username == '' or password == '' or verify == '':
            flash('One or more fields are invalid. All fields must be complete', 'error')
            errors = True

        elif existing_user and existing_user.username == username:
            flash('Yikes! That username already exists.', 'error')
            errors = True

        elif len(username) <3:
            flash('INVALID USERNAME - Come on man, the username has to be more than 3 characters!', 'error')
            errors = True

        elif len(password) <3:
            flash('INVALID PASSWORD - Get it together! Your password has to be more than 3 characters!', 'error')
            errors = True
        
        elif password != verify:
            flash('PASSWORDS DO NOT MATCH - Hey, fat fingers. Try again!', 'error') 
            errors = True

        if errors:
            return redirect('/signup')

        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
      

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect ('/blog')


@app.route('/')
def index():
    
    users= User.query.all()
    selected_user = request.args.get('id')
    if selected_user != None:
        user = User.query.get(selected_user)
        blogs = Blog.query.filter_by(owner_id=selected_user)
        return render_template('singleUser.html', user=user, blogs=blogs)

    return render_template('index.html', title= "Blogz!", users=users, selected_user=selected_user)
#go back and ask why we have user=user in render templates.

@app.route('/blog', methods = ['POST', 'GET'])
def blogs():
        
    blogs= Blog.query.all()
    
    return render_template('blogs.html', title= "Blogz!", blogs = blogs)
  

@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():

    if request.method == 'GET':
        return render_template('addentry.html', title= "Blogz!")

    elif request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        owner = User.query.filter_by(username=session['username']).first()
        blog = Blog(blog_title,blog_body, owner)

        errors = False
        
        if blog_title == '' and blog_body == '':
            flash("Everything is blank! Try again.", 'error')
            errors = True
        
        elif blog_title =='':
            flash("Yikes! You forgot to add a title to your blog post!",'error')
            errors = True
        elif blog_body == '':
            flash("Whoops! You need to write your post here.",'error')
            errors = True

        if errors:
            return redirect('/newpost')       
        
        db.session.add(blog)
        db.session.commit()

    return render_template('post.html', blog= blog)
        
# @app.route('/user')
# def user_posts():

#     # owner= User.query.filter_by(id=user_id).first()

#     # blogs = Blog.query.filter_by(owner_id).all()
# #     # user_id = request.args.get('user_id')

#     return render_template('singleuser.html', blogs = blogs)

# @app.route('/post')
# def post(blog_id):

#     blog= Blog.query.filter_by(id=blog_id).one()
#     blog_id = request.args.get('blog_id')

#     return redirect("/post?blog_id")

@app.route('/post/<int:blog_id>')
def post(blog_id):

    blog= Blog.query.filter_by(id=blog_id).one()

    return render_template('post.html', blog = blog)


  

if __name__ == '__main__':
    # this gets added because of the import of the database
    app.run()