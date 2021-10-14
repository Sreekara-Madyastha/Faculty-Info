
from flask import Flask, render_template, request, redirect, session
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
    mycursor.execute('SELECT timetable.Day,timetable.Stime,timetable.Room,timetable.DurationMins,faculty.FName FROM ((timetable INNER JOIN taughtby ON taughtby.CId=timetable.CId) INNER JOIN faculty ON taughtby.FId=faculty.FId) WHERE (taughtby.CId=%s AND taughtby.Semester LIKE %s)',(request.form.get('selected_course'),'%'))
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

@app.route("/")
@app.route("/home")
def begin():
    return render_template("home.html",departments=departments,fac=fac,sem=sem)

       

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login_validation', methods=['POST'])
def login_validation():
    Username = request.form.get('Username')
    password = request.form.get('password')

    mycursor.execute("""select * from `authorizedPersonell` where `Username` = '{}' and `Password` = '{}'""".format(Username, password))
    users = mycursor.fetchall()

    if len(users) > 0:
        session['AId'] = users[0][0]
        return redirect('/access')
    else:
        return render_template('login.html', error_message="Invalid Username or Password")


@app.route('/access')
def home():
    if 'AId' in session:
        return render_template('access.html')
    else:
        return redirect('/login')


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


if __name__ == '__main__':
  app.run(debug=True)

