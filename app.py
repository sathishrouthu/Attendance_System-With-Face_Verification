from sre_constants import SUCCESS
from flask import *
from flask_mysqldb import MySQL
import datetime
import os
import recognizer
import datetime

app = Flask(__name__)

app.secret_key= "sathishrouthu5482"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'sathish'
app.config['MYSQL_PASSWORD'] = 'Sathish@5482'
app.config['MYSQL_DB'] = 'sathish'
app.config['UPLOAD_FOLDER']="./Images/"

mysql = MySQL(app)


@app.route('/',methods=['GET','POST'])
def home():
    return render_template('index.html')

@app.route('/takeattendance',methods=['POST','GET'])
def takeattendance():
    if request.method=='POST' and request.form['period']!='Select Subject':
        branch = request.form['branch']
        year = request.form['year']
        section = request.form['section']
        period = request.form['period']
        Date = datetime.datetime.now().strftime("%Y-%m-%d")
        Studentids = recognizer.Recognizer()
        #Creating a connection cursor
        cursor = mysql.connection.cursor()
        #Executing SQL Statements
        for sid in Studentids:
            cursor.execute(''' INSERT INTO attendance VALUES (%s,%s,%s,'present') ''',(Date,sid.upper(),period))
            mysql.connection.commit()
        cursor.execute(''' Select StudentID FROM Students WHERE BRANCH=%s AND YEAR=%s AND SECTION=%s ''',(branch,year,section))
        allstudentids =cursor.fetchall()
        for sid in allstudentids:
            if sid[0].upper() not in Studentids:
                ret = cursor.execute(''' INSERT INTO attendance VALUES (%s,%s,%s,'absent') ''',(Date,sid[0].upper(),period))
            mysql.connection.commit()
        #Saving the Actions performed on the DB
        #Closing the cursor
        cursor.close()
        return render_template('index.html',msgs=Studentids)

    return redirect('/')


@app.route('/addstudent',methods=['GET','POST'])
def addstudent():
    if request.method=='POST':
        StudentID = request.form['studentid']
        StudentName= request.form['name']
        Branch = request.form['branch']
        Year = request.form['year']
        Section = request.form['section']
        img = request.files['image']
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], img.filename.upper()))
        cursor = mysql.connection.cursor()
        #Executing SQL Statements
        try:
            cursor.execute(''' INSERT INTO students VALUES(%s,%s,%s,%s,%s) ''', (StudentID.upper(),StudentName,Branch.upper(),Year,Section))
        except:
            cursor.close()
            return "Failed to insert"
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        
        #Closing the cursor
        cursor.close()
        return "Success"
    return redirect('/')
    
@app.route('/search',methods=['GET','POST'])
def search():
    if request.method == 'POST':
        branch=request.form['branch']
        year=request.form['year']
        section=request.form['section']
        date= str(request.form['date'])
        period = request.form['period']
        cursor = mysql.connection.cursor()
        clas = year+"year" +" - " + branch+" - " + section
        try:
            #Executing SQL Statements
            cursor.execute(''' SELECT s.StudentID , s.Name , a.status FROM students as s INNER JOIN attendance as a ON  s.StudentID=a.Studentid where DATE = %s AND  period = %s AND Year = %s AND BRANCH=%s AND Section = %s; ''', (date,period,year,branch,section) )
            qresults = cursor.fetchall()
        except:
            cursor.close()
            return "Failed to Retrieve"
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()
        return render_template('search.html',clas = clas,date=date,period=period,results= qresults )
    return render_template('search.html')


if __name__=='__main__':
    app.run(debug=True)