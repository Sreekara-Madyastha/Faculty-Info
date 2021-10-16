from flask import Flask, render_template, request, redirect, session,jsonify
from flask_session import Session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(10)
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Sreek@r123",
  database="courses_faculty"
)
mycursor=mydb.cursor()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
def my_function(x):
  return list(dict.fromkeys(x))


def greater(a,b):
  [sem1,year1]=a.split(" ")
  [sem2,year2]=b.split(" ")
  if(year1==year2):
    if sem1=='Autumn' and sem2=='Spring':
      return False
    else:
      return True
  else:
    return year1<year2
def filter(result,sem1,sem2):
  sol=[]
  if sem1=="":
    return result
  else:
    if sem2=="":
      for i in result:
        if greater(sem1,i[4])==True:
          sol+=i
    else:
      for i in result:
        if greater(sem1,i[4])==True and greater(i[4],sem2):
          sol.append(i)
    return sol
      

@app.route('/search',methods=["GET","POST"])
def search():
  sem1=request.form.get('fromsem')
  sem2=request.form.get('tillsem')
  if request.form.get('facselect')!="" :
    mycursor.execute('SELECT taughtby.CId,courses.CName,taughtby.FId,faculty.FName,taughtby.Semester,taughtby.NumStudents FROM ((taughtby INNER JOIN courses ON courses.CId=taughtby.CId) INNER JOIN faculty ON taughtby.FId=faculty.FId) WHERE( courses.DId LIKE %s AND taughtby.FId LIKE %s)',('%'+request.form.get('depselect')+'%',request.form.get('facselect')))
    result=mycursor.fetchall()
    result=filter(result,sem1,sem2)
  else:
    mycursor.execute('SELECT taughtby.CId,courses.CName,taughtby.FId,faculty.FName,taughtby.Semester,taughtby.NumStudents FROM ((taughtby INNER JOIN courses ON courses.CId=taughtby.CId) INNER JOIN faculty ON taughtby.FId=faculty.FId) WHERE( courses.DId LIKE %s AND taughtby.FId LIKE %s)',('%'+request.form.get('depselect')+'%',"%"))
    result=mycursor.fetchall()
    result=filter(result,sem1,sem2)
  # print(result)
  return render_template('home.html',result=result,FId=request.form.get('facselect'),DId=request.form.get('depselect'),tillsem=request.form.get('tillsem'),fromsem=request.form.get('fromsem'),departments=departments,fac=fac,sem=sem)

@app.route('/coursesearch',methods=["GET","POST"])
def course():
  if request.form.get('selected_course')!="":
    mycursor.execute('SELECT timetable.CId,timetable.Day,timetable.Stime,timetable.Room,timetable.DurationMins,faculty.FName FROM ((timetable INNER JOIN taughtby ON taughtby.CId=timetable.CId) INNER JOIN faculty ON taughtby.FId=faculty.FId) WHERE (taughtby.CId=%s AND taughtby.Semester LIKE %s)',(request.form.get('selected_course'),'%'))
    courstim=mycursor.fetchall()
    return render_template('home.html',courstim=courstim, departments=departments)
  else:
    mycursor.execute('SELECT * FROM courses WHERE DId=%s',(request.form.get('depforcourse'),))
    coursesel=mycursor.fetchall()
    return render_template('home.html',coursesel=coursesel, departments=departments)



mycursor.execute('SELECT * FROM departments')
departments=mycursor.fetchall()
mycursor.execute('SELECT Semester FROM taughtby')
sem=mycursor.fetchall()
sem = my_function(sem)
mycursor.execute('SELECT * from faculty')
fac=mycursor.fetchall()
mycursor.execute('SELECT * FROM courses')
c=mycursor.fetchall()
mycursor.execute('SELECT * FROM timetable')
tit=mycursor.fetchall()
@app.route("/")
@app.route("/home")
def begin():
    return render_template("home.html",departments=departments,fac=fac,sem=sem,c=c,tit=tit)

       

@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/logout')
def logout():
    session['AId']=None
    return redirect('/home')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    Username = request.form.get('Username')
    password = request.form.get('password')
    mycursor.execute('SELECT * FROM authorizedPersonell WHERE Username=%s AND Password=%s',(Username,password))
    users = mycursor.fetchall()
    if users:
        session['AId'] = users[0][0]
        return redirect('/home')
    else:
        return render_template('login.html', error_message="Invalid Username or Password")


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/add_user', methods=['POST'])
def add_user():
    addUsername = request.form.get('reg_Username')
    addEmail = request.form.get('reg_Email')
    addPassword = request.form.get('reg_Password')

    mycursor.execute("""insert into `authorizedPersonell` (`Username`, `Email`, `Password`) values
             ('{}', '{}', '{}')""".format(addUsername, addEmail, addPassword))
    mydb.commit()

    return render_template('login.html', after_reg_message="Account created successfully! Login to proceed")

@app.route('/change',methods=["GET","POST"])
def change():
  operation=request.form.get('operation')
  changeon= request.form.get('changeon')
  if operation=="deletion":
      mycursor.execute('SELECT * FROM timetable WHERE Day=%s AND Room=%s AND STime=%s AND CId=%s',(request.form.get('dday'),request.form.get('rroom'),request.form.get('sstime'),request.form.get('ccid')))
      look=mycursor.fetchall()
      if(look==[]):
        return render_template("home.html",departments=departments,fac=fac,sem=sem,c=c,error="there is no such course at given time")
      else:
        mycursor.execute('DELETE FROM timetable WHERE Day=%s, Room=%s AND STIme=%s',(request.form.get('dday'),request.form.get('rroom'),request.form.get('sstime')))
        mydb.commit()
        return redirect('/')
  elif operation=="insertion":
    if changeon=="Faculty_Info":
        mycursor.execute('INSERT INTO faculty(FName) values(%s)',(request.form.get('newfacname'),))
        mydb.commit()
        return redirect('/')
    elif changeon=="course_Info":
      mycursor.execute('SELECT * FROM courses WHERE CId=%s',(request.form.get('newcourse')))
      look=mycursor.fetchall()
      if(look!=[]):
        return render_template("home.html",departments=departments,fac=fac,sem=sem,c=c,error="Course with same courseID already exists")
      else:
        mycursor.execute('INSERT INTO courses(CId,CName,DId) values(%s,%s,%s)',(request.form.get('newcourse'),request.form.get('cname'),request.form.get('ofdep')))
        mydb.commit()
        return redirect('/')
    elif changeon=="teaching_Info":
      mycursor.execute('INSERT into taughtby(CId,FId,Semester,NumStudents) values (%s,%s)',(request.form.get('class'),request.form.get('teacher'),request.form.get('semofnewcourse'),request.form.get('noofstuds')))
      mydb.commit()
      return redirect('/')
    elif changeon=="timings":
      mycursor.execute('SELECT * FROM timetable WHERE Day=%s AND STime=%s AND ROOM=%s',(request.form.get('day'),request.form.get('starttime'),request.form.get('room')))
      look=mycursor.fetchall()
      if look!=[]:
        return render_template("home.html",departments=departments,fac=fac,sem=sem,c=c,error="There already exists on same day same room at that time")
      else:
        mycursor.execute('INSERT into timetable(Day,STime,Room,CId,DurationMins)values(%s,%s,%s,%s,%s)',(request.form.get('day'),request.form.get('starttime'),request.form.get('room'),request.form.get('courseoftime'),request.form.get('dur')))
        mydb.commit()
        return redirect('/')
  elif operation=="updation":
    mycursor.execute('SELECT * FROM timetable WHERE Day=%s AND STime=%s AND ROOM=%s',(request.form.get('dday'),request.form.get('sstime'),request.form.get('rroom')))
    look=mycursor.fetchall()
    if look==[]:
      return render_template("home.html",departments=departments,fac=fac,sem=sem,c=c,error="There is no course at given time")
    else:
      mycursor.execute('UPDATE timings SET CId=%s',(request.form.get('ccid')))
      mydb.commit()
      return redirect('/')
  return redirect('/')
@app.route('/dept/<department>')
def dept(department):
  mycursor.execute('SELECT DISTINCT taughtby.FId,faculty.FName FROM ((taughtby INNER JOIN courses ON courses.CId=taughtby.CId) INNER JOIN faculty ON taughtby.FId=faculty.FId) WHERE( courses.DId LIKE %s AND taughtby.FId LIKE %s)',('%'+department+'%',"%"))
  result=mycursor.fetchall()
  print(result)
  res=[]
  for r in result:
    resobj={}
    resobj['id']=r[0]
    resobj['name']=r[1]
    res.append(resobj)

  return jsonify({'depts' : res})

if __name__ == '__main__':
  app.run(debug=True)

