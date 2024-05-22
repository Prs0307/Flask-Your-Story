import math
from flask import Flask, redirect , render_template,request,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import os
from werkzeug.utils import secure_filename
import json
import mysql.connector



local_server = True
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        params = json.load(f)["params"]
except FileNotFoundError:
    print("File not found.")
except json.JSONDecodeError as e:
    print("Error decoding JSON:", e)
except Exception as e:
    print("An error occurred:", e)

# with open('config.json','r') as c:
#     params = json.load(c)["params"]




app = Flask(__name__)
# Details on the Secret Key: https://flask.palletsprojects.com/en/2.3.x/config/#SECRET_KEY
# NOTE: The secret key is used to cryptographically-sign the cookies used for storing
#       the session data.
app.secret_key = 'BAD_SECRET_KEY'

app.config['UPLOAD_FOLDER']= params['upload_location']
# Check if the directory exists, if not create it
upload_folder = params['upload_location']
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)




app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT ='465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['user_gmail'],
    MAIL_PASSWORD =params['g_password']

)
print(params['user_gmail']+' '+params['g_password'])
mail = Mail(app)
# configure the SQLite database, relative to the app instance folder
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/yourstory'

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
    print(params)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['production_uri']

# initialize the app with the extension
db = SQLAlchemy(app)




class Contact(db.Model):
    '''
    sno , name,email, phone,date,
    '''
    sno=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(20),nullable=False)
    phoneno=db.Column(db.String(12), nullable=False)
    msg=db.Column(db.String(50),nullable=False)
    date=db.Column(db.Date, nullable=True)

class  Post(db.Model):
    '''
    sno , name,email, phone,date,
    '''
    sno=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(50),nullable=False)
    subheading=db.Column(db.String(20),nullable=False)
    slog=db.Column(db.String(22), nullable=False)
    content=db.Column(db.String(150),nullable=False)
    date=db.Column(db.Date, nullable=True)
    img_url=db.Column(db.String(50),nullable=False)


@app.route('/login')
def index():
    try:
        posts = Post.query.filter_by().all()
        # [0:params['no_of_posts']]
    except Exception as e:
         posts = []  # If there's an error, provide an empty list
         print("Error fetching posts:", e)
    return render_template('login.html',params=params,posts=posts)
@app.route('/')
def signin():
    if (not 'user' in session and session['user']==params['admin_email']) :
     return redirect('/login')
    else:
     return redirect('/dashboard')
@app.route('/home')
def home():
    if ('user' in session and session['user']==params['admin_email']) :
    
            try:
                posts = Post.query.filter_by().all()
                # [0:params['no_of_posts']]
            except Exception as e:
                posts = []  # If there's an error, provide an empty list
                print("Error fetching posts:", e)
            last=math.ceil(len(posts)/int(params['no_of_posts']))
            page=request.args.get('page')
            if (not str(page).isnumeric()):
                page=1
            page=int(page)
            posts=posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
            if(page==1):
                prev="#"
                next="/?page="+str(page+1)
            elif(page==last):
                next="#"
                prev="/?page="+str(page-1)
            else:
                prev="/?page="+str(page-1)
                next="/?page="+str(page+1)
         

            return render_template('index.html',params=params,posts=posts,prev=prev,next=next)
    return redirect('/login')


@app.route('/about')
def about():
    return render_template('about.html',params=params)
@app.route('/dashboard',methods=['GET', 'POST'])
def login():
    if ('user' in session and session['user']==params['admin_email']) :
             posts = Post.query.all()
             return render_template('dashboard.html',params=params,posts=posts)
    if request.method == 'POST':
        uname = request.form.get('username')
        password = request.form.get('password')
        if ((uname == params['admin_email']) and  password==params['admin_password']): 
                                # CREATE SESSION VARIABLES
                                session['user']=uname
                                posts = Post.query.all()
                                return render_template('dashboard.html',params=params,posts=posts)
        else: 
             return f'''<h5>Error : Invalid username or password</h5>\n <a href="/"> Try again </a>'''
    else:
        return render_template('login.html',params=params)

@app.route('/contact',methods=['Get','POST'])
def contact():
    if(request.method == 'POST'):
        '''Fetch Entry from f e '''
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phoneno')
        message=request.form.get('msg')


        '''ENTRY TO DATABASE      class= entries'''    
        entry = Contact(name=name,phoneno=phone,msg=message,email=email,date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message("New Message From "+name,
                         sender=email,recipients=["princesahu169@gmail.com"],
                         body = message + "\n" + phone + "\n"
        )
    return render_template('contact.html',params=params)

@app.route("/posts/<string:post_slug>", methods=['GET'])
def posts_route(post_slug):
    post = Post.query.filter_by(slog=post_slug).first()
    print(post.title)
    return render_template('post.html',params=params,post=post)

@app.route("/edit/<string:sno>", methods=['POST','GET'])
def modify(sno):
       if ('user' in session and session['user']==params['admin_email']) :
            if(request.method == 'POST'):
                 
                 prev_title =  request.form.get('title')
                 subheading = request.form.get('subheading')
                 slog=request.form.get('slug')
                 content=request.form.get('content')
                 img_url=request.form.get('img_url')
                 
    # date=db.Column(db.Date, nullable=True)


            
                 if(sno=='0'):
                      post=Post(sno=sno,title=prev_title,subheading=subheading,slog=slog,content=content,img_url=img_url,date=datetime.now())
                      db.session.add(post)
                      db.session.commit()
                 else:
                      post = Post.query.filter_by(sno=sno).first()
                      if post:
                        post.title=prev_title
                        post.subheading=subheading
                        post.slog=slog
                        post.content=content
                        post.img_url=img_url
                        post.date=datetime.now()

                        db.session.commit()
                      else:
                         post=Post(sno=sno,title=prev_title,subheading=subheading,slog=slog,content=content,img_url=img_url,date=datetime.now())
                         db.session.add(post)
                         db.session.commit()
                         return redirect('/dashboard')
                      return render_template('edit.html',post=post, sno=sno, params=params, content=content, img_url=img_url,slog=slog,datetime=datetime.now())
            else:
                post = Post.query.filter_by(sno=sno).first() if sno != '0' else None
                return render_template('edit.html', post=post, sno=sno, params=params)
            return redirect('/dashboard')
            # return '<div style="text-align: center; margin:0 auto;"><h1>post method Not found</h1></div>'

@app.route("/delete/<string:sno>")
def delete(sno):
    if ('user' in session and session['user']==params['admin_email']) :
                  
        post = Post.query.filter_by(sno=sno).first() 
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


# Uploader

@app.route('/uploadfile1',methods=['POST'])
def uploader():
    
    if('user' in session and session['user']== params['admin_email']):
         if(request.method== 'POST'):
            
              f=request.files['file1']
              f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
              print("UPLOAD_FOLDER:", app.config['UPLOAD_FOLDER'])
              print("Filename:", f.filename)
              return "UPLOAD_SUCCESS"
         

          

@app.route("/posts")
def posts():
        if ('user' in session and session['user']==params['admin_email']) :
             posts = Post.query.all()
             return render_template('userpost.html',params=params,posts=posts)


app.run(port=2000, debug=True)