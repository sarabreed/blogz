from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'

#mysql+pymysql://username:password@port/database


app.config['SQLALCHEMY_ECHO'] = True
#this lets you see the sql from behind the scenes

db = SQLAlchemy(app)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

#creating a persistent class that can be put in the database.
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

#look at flick-list as well
#this sets the default value
    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods = ['POST', 'GET'])
def index():
    
    blogs= Blog.query.all()

    return render_template('index.html', title= "Build a Blog!", blogs=blogs)
  

@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():

    if request.method == 'GET':
        return render_template('addentry.html', title= "Build a Blog!")

    elif request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        
        errors = False

        # if blog_title =='' and blog_body =='':
        #     flash ("Uh oh! You forgot to do anything with this post", 'error')
        #     #return redirect('/newpost')
        #     errors = True
        
        if blog_title == '' and blog_body == '':
            flash("Everything is blank! Try again.", 'error')
            errors = True
        
        elif blog_title =='':
            flash("Yikes! You forgot to add a title to your blog post!",'error')
            #return redirect('/newpost')
            errors = True
        elif blog_body == '':
            flash("Whoops! You need to write your post here.",'error')
            #return redirect('/newpost')
            errors = True

        if errors:
            return redirect('/newpost')
        
            

        blog = Blog(blog_title,blog_body)
        db.session.add(blog)
        db.session.commit()

    return render_template('post.html', blog= blog)
        

@app.route('/post/<int:blog_id>')
def post(blog_id):

    blog= Blog.query.filter_by(id=blog_id).one()

    return render_template('post.html', blog = blog)
  
# @app.route('/post/<int:post_id>')
# def post(post_id):
#     post = Blogpost.query.filter_by(id=post_id).one()

#     return render_template('post.html', post=post)

    # 
    # return render_template('addentry.html',title="Build a Blog", 
    #     title = title, body=body)


# @app.route('/blog', methods = ['POST'])
# def validate_fields():
#     title = request.addentry['title']
#     body = request.addentry['body']


#     title_error = ''
#     body_error = ''

#     if title == '':
#         title_error = "You forgot to add a title to your blog post."
#         title = ''
    
#     if body == '':
#         body_error ="Whoops! You need to write your post here."
#         body = ''

#     if title_error != '' or body_error != '':

#         return render_template('addentry.html', title = title, title_error = title_error, body = body, body_error=body_error)

#     else:
#         return "YES"




if __name__ == '__main__':
    # this gets added because of the import of the database
    app.run()