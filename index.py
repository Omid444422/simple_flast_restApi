import flask
import json
import hashlib
import os
from werkzeug.utils import secure_filename
from modules.Database import Database
import time

MAIN_FOLDER = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = f'{MAIN_FOLDER}\\uploads\\'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','tiff'}


def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.get('/api/users')
def users():
  db = Database()
  result =  {'data':db.querySingle('SELECT * FROM users',[]),'status':200}
  return result

@app.get('/api/users/<id>')
def get_user_by_id(id):
  if int(id) >= 0:
      db = Database()
      result = {'data':db.querySingle('SELECT * FROM users WHERE id=%s',[id]),'status':200}
      return result
  

@app.put('/api/users/<id>')
def update_user_by_id(id):
  db = Database()
  now = time.time()
  if int(id) > 0:
    if flask.request.method == 'PUT':
      try:
        username = flask.request.form['username']
        password = flask.request.form['password']
        avatar = flask.request.files['avatar']
        role = flask.request.form['role']
      except:
        return {'message':'cant find correct fields'}
      
    if username == '' or password == '' or int(role) <= 0:
      return {'message':'fill out the form please'}
    
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    if avatar.filename != '':
      old_file = db.querySingle('SELECT avatar FROM users WHERE id=%s',[id])
      old_file_path = str(old_file[0]['avatar'])
      
      if os.path.exists(old_file_path):
        os.remove(old_file_path)

      if avatar and allowed_file(avatar.filename):
        filename = secure_filename(avatar.filename)
        avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], str(now) + filename))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(now) + filename)
        
      db.querySingle('UPDATE users SET username=%s , password=%s , avatar=%s , role=%s WHERE id=%s',[username,hashed_password,file_path,role,id])
      return {'status':'successfull'}

@app.post('/api/users/create')
def create_new_user():
  if flask.request.method == 'POST':
    try:
      db = Database()
      now = time.time()
      username = flask.request.form['username']
      password = flask.request.form['password']
      avatar = flask.request.files['avatar']
      is_active = 0
      role = 1
    except:
      return {'message':'cant find the correct field'}
    
    if username == '' or password == '' or avatar.filename == '':
      return {'message':'please fill out the form'}
    
    username_exist = db.cursor.execute(f'SELECT * FROM users WHERE username="{username}"')

    if db.cursor.rowcount > 0:
      return {'message':'this username is exist'}

  h = hashlib.sha256()
  h.update(password.encode('utf8'))
  h.hexdigest()
  hash_password = h.hexdigest()
  if avatar.filename != '' and allowed_file(avatar.filename) != '':
        filename = secure_filename(avatar.filename)
        avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], str(now) + filename))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(now) + filename)
        
        db.querySingle('INSERT INTO users (id,username,password,avatar,is_active,role) VALUES (%s,%s,%s,%s,%s,%s)',['NULL',username,hash_password,file_path,is_active,role])
        return {'status':'successfull'}
  


@app.delete('/api/users/<id>')
def delete_user_by_id(id):
  if(id):
    db = Database()
    db.cursor.execute(f'SELECT avatar FROM users WHERE id={id}')
    if(db.cursor.rowcount > 0):
      avatar_url = db.cursor.fetchall()
      if os.path.exists(avatar_url[0][0]):
        os.remove(avatar_url[0][0])
      
    db.querySingle('DELETE FROM users WHERE id=%s',[id])
    return {'status':'successfull'}
  else:
    return {'message':'id param error where is id ? exacly'}

# posts
@app.get('/api/posts')
def get_posts():
  db = Database()
  result = {'data':db.querySingle('SELECT * FROM posts INNER JOIN users ON users.id = posts.user_id WHERE is_show=%s',[1]),'status':200}
  return result

@app.get('/api/posts/<id>')
def get_posts_by_id(id):
  if id:
    db = Database()
    result = {'data':db.querySingle('SELECT * FROM posts WHERE id=%s',[id])}
    return result
  


@app.put('/api/posts/<id>')
def update_posts_by_id(id):
  if id:
    db = Database()
    now = time.time()
    if flask.request.method == 'PUT':

      try:
        # form requests
        post_title = flask.request.form['title']
        post_desc = flask.request.form['description']
        post_cat = flask.request.form['cat_id']
        post_avatar = flask.request.files['post_avatar']
        post_is_show = 1
      # param request
        user_id = flask.request.args.get('user_id')
      except:
        return {'message':'cant find correct field'}
      

    if post_title == '' or post_desc == '' or post_avatar.filename == '':
      return {'message':'please fill out the form'}
    
    check_exist = db.querySingle('SELECT * FROM posts WHERE title=%s',[post_title])
    if check_exist:
      return {'message':f'this title:{post_title} is already exist'}
    
    if post_avatar.filename != '':
      old_file = db.querySingle('SELECT post_avatar FROM posts WHERE id=%s',[id])
      old_file_path = str(old_file[0]['post_avatar'])
  
      if os.path.exists(old_file_path):
        os.remove(old_file_path)
    
    if post_avatar.filename != '' and allowed_file(post_avatar.filename):
        filename = secure_filename(post_avatar.filename)
        post_avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], str(now) + filename))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(now) + filename)

        db.querySingle(f'UPDATE posts SET title=%s,description=%s,post_avatar=%s,is_show=%s,user_id=%s,cat_id=%s WHERE id={id}',[post_title,post_desc,file_path,post_is_show,user_id,post_cat])
        return {'status':'success'}
    

@app.post('/api/posts/create')
def create_new_post():
  db = Database()
  now = time.time()
  # requests forms
  if flask.request.method == 'POST':
    try:
      post_title = flask.request.form['title']
      post_desc = flask.request.form['desc']
      post_avatar = flask.request.files['post_avatar']
      post_cat_id = int(flask.request.form['cat_id'])
      post_is_show = 1
      # requests param
      post_user_id = flask.request.args.get('user_id')
    except:
      return {'message':'error cant find correct field'}
    
    if post_title == '' or post_desc == '' or post_avatar.filename == '' or post_cat_id <= 0:
      return {'message':'fill out the form'}
    
    check_exist = db.querySingle('SELECT * FROM posts WHERE title=%s',[post_title])
    if check_exist:
      return {'message':f'this title:{post_title} is already exist'}

    if post_avatar.filename != '' and allowed_file(post_avatar.filename):
        filename = secure_filename(post_avatar.filename)
        post_avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], str(now) + filename))
        file_path = '~\\' + os.path.join(app.config['UPLOAD_FOLDER'], str(now) + filename)

        db.querySingle('INSERT INTO posts (id,title,description,post_avatar,is_show,user_id,cat_id) VALUES (%s,%s,%s,%s,%s,%s,%s)',['NULL',post_title,post_desc,file_path,post_is_show,post_user_id,post_cat_id])
        
        return {'status':'successfull','status_code':200}
    
@app.delete('/api/posts/<id>')
def delete_post(id):
    if id:
      db = Database()
      exist_post = db.querySingle('SELECT * FROM posts WHERE id=%s',[id])
      if exist_post:
        db.querySingle('DELETE FROM posts WHERE id=%s',[id])
        return {'status':'successfull','status_code':200}
      else:
        return {'message':'something went wrong'}
      
@app.get('/api/category')
def get_all_category():
  db = Database()
  result = {'data':db.querySingle('SELECT * FROM categories WHERE is_active=%s',[1]),'status':200}
  return result

@app.get('/api/category/<id>')
def get_all_posts_category(id):
  if id:
    db = Database()
    result = {'data':db.querySingle('SELECT * FROM posts WHERE cat_id=%s',[id]),'status':200}
    return result

app.run(debug=True,port=8080)


