# importing required Modules

from flask import Flask, render_template, request, redirect, Response
from flask_mail import Mail, Message
import random
import pymysql
import sqlite3
import os
import io
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import statistics

# Global Variables

global teacher_Id, student_Id, quiz_Id
global presentQuestion
global totalQuestions
global Questions
global eTime
global flag
global random_number
global mail_id
global teacherName
teacher_Id = None
student_Id = None
quiz_Id = None
global flag
flag = 0
# Initializing Flask Application
app = Flask(__name__)

# Fetching the Password of the Database from the Txt file
PASSWORD = ''
with open('Details.txt', 'r') as f:
    PASSWORD = f.readline()


# Function to generate a random string of length 4
def CreateQuizId():
    lst = []
    for i in range(4):
        lst.append(str(chr(random.randint(65, 90))))
    print(lst)
    QuizId = ""
    for x in lst:
        QuizId += x
    return QuizId


# Application Default Route
@app.route("/", methods=["GET", "POST"])
def index():
    # Connecting to MySQL Database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    # If Exception occurred redirecting to default route
    except Exception as E:
        print(E)
        return render_template("index.html", noNetwork=True)
    cur = conn.cursor()
    cur.execute('''SELECT PASSWORD, PORT, SEREVER, USERNAME, DB FROM EMAIL WHERE PORT=587''')
    data = cur.fetchall()[0]
    # Configuring the Mail Credentials from Database
    app.config["MAIL_PASSWORD"] = data[0]
    app.config["MAIL_PORT"] = data[1]
    app.config["MAIL_SERVER"] = data[2]
    app.config["MAIL_DEFAULT_SENDER"] = data[3]
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = data[4]
    conn.commit()
    conn.close()
    return render_template("index.html")


# Login route
@app.route("/login", methods=["POST", "GET"])
def login():
    global presentQuestion, totalQuestions, Questions, flag
    global teacher_Id, student_Id, quiz_Id, teacherName, eTime
    uName = request.form.get("username")
    pwd = request.form.get("password")
    name = ""
    quizId = request.form.get("quizId")
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return render_template("index.html", uName=uName, pwd=pwd, quizId=quizId, noNetwork=True)
    cur = conn.cursor()
    # Teacher login
    if quizId == "" or quizId is None:
        # Selecting Details of teacher with their Email-Id
        cur.execute('''SELECT * FROM TEACHER WHERE EMAIL='{}' '''.format(uName))
        details = cur.fetchall()
        # Committing And Closing Database Connection
        conn.commit()
        conn.close()
        print(details)
        if details and (quizId == "" or quizId is None):
            name = details[0][1] + " " + details[0][2]
            teacherName = name
            Password = details[0][6]
            # If Password Matched
            if pwd == Password:
                teacher_Id = uName
                return render_template("teacherHome.html", username=teacherName)
            # If Password is Wrong
            else:
                return render_template("teacher.html", wrngPwd=True, uName=uName, pwd=pwd)
        # If Teacher do not Exist
        else:
            return render_template("teacher.html", userNotFound=True, uName=uName, pwd=pwd)
    # Student Login
    if quizId != "" and quizId is not None:
        # Selecting Student Details from the Database
        cur.execute('''SELECT * FROM STUDENT WHERE QUIZ_ID='{}' AND EMAIL='{}' '''.format(quizId, uName))
        details = cur.fetchall()
        conn.commit()
        # If Student Exists
        if details:
            cur.execute('''SELECT * FROM STUDENT WHERE QUIZ_ID='{}' AND EMAIL='{}' '''.format(quizId, uName))
            details = cur.fetchall()
            conn.commit()
            if details[0][0] == uName:
                # If Password Matched
                if pwd == details[0][2]:
                    print("Password Matched...")
                    student_Id = uName
                    quiz_Id = quizId
                    conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                                           passwd=PASSWORD, database="DBMSFLASKPROJECT")
                    cur = conn.cursor()
                    # Fetching the Quiz Details from the DataBase
                    cur.execute('''SELECT * FROM QUIZ WHERE QUIZ_ID='{}' '''.format(quizId))
                    d = cur.fetchall()
                    conn.commit()
                    conn.close()
                    # Flag to check whether the student have done malpractice or not
                    if int(flag) <= 2:
                        pass
                    else:
                        return redirect("submitted")
                    student_Id = uName

                    conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                           user="DARKKNIGHT",
                                           passwd=PASSWORD, database="DBMSFLASKPROJECT")
                    cur = conn.cursor()
                    # Fetching Student Details from the Database
                    cur.execute(
                        '''SELECT NAME,EMAIL FROM STUDENT WHERE QUIZ_ID='{}' AND EMAIL='{}' '''.format(quizId, uName))
                    student = cur.fetchall()
                    data = d[0][3].split("T")
                    startDate = data[0]
                    print(startDate)
                    startTime = data[1]
                    print(startTime)
                    endData = d[0][4].split("T")
                    endTime = endData[1]
                    print(endTime)
                    startHrs = startTime[:2]
                    startMins = startTime[3:]
                    endHrs = endTime[:2]
                    endMins = endTime[3:]
                    # If Quiz Date Matched
                    if datetime.now().strftime("%Y-%m-%d") == startDate:
                        # If Student Logins in Time
                        if startHrs == datetime.now().strftime("%H") and startMins <= datetime.now().strftime("%M"):
                            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                                   user="DARKKNIGHT",
                                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
                            cur = conn.cursor()
                            cur.execute('''SELECT FLAG FROM STUDENT WHERE QUIZ_ID='{}' AND EMAIL='{}' '''.format(quizId,
                                                                                                                 uName))
                            # Checking Whether the Student has submitted the quiz before or not
                            if cur.fetchall()[0][0] == "S":
                                something = "Student, you have already submitted your quiz. "
                                return render_template("studentlogin.html", data=d, student=student,
                                                       something=something)
                            # If not Submitted directing to the Instructions Page
                            else:
                                return render_template("instructions.html", data=d, student=student)
                        elif startHrs < datetime.now().strftime("%H") < endHrs:
                            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                                   user="DARKKNIGHT",
                                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
                            cur = conn.cursor()
                            cur.execute('''SELECT FLAG FROM STUDENT WHERE QUIZ_ID='{}' AND EMAIL='{}' '''.format(quizId,
                                                                                                                 uName))
                            if cur.fetchall()[0][0] == "S":
                                # print(cur.fetchall()[0][0])
                                something = "Student, you have already submitted your quiz. "
                                return render_template("studentlogin.html", data=d, student=student,
                                                       something=something)
                            else:
                                return render_template("instructions.html", data=d, student=student)
                            pass
                        elif endHrs == datetime.now().strftime("%H") and endMins > datetime.now().strftime("%M"):
                            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                                   user="DARKKNIGHT",
                                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
                            cur = conn.cursor()
                            cur.execute(
                                '''SELECT FLAG FROM STUDENT WHERE QUIZ_ID='{}' AND EMAIL='{}' '''.format(quizId, uName))
                            if cur.fetchall()[0][0] == "S":
                                something = "Student, you have already submitted your quiz. "
                                return render_template("studentlogin.html", data=d, student=student,
                                                       something=something)
                            else:
                                return render_template("instructions.html", data=d, student=student)
                            pass
                        else:
                            something = "quiz has ended"
                            return render_template("studentlogin.html", data=d, something=something, student=student)
                    else:
                        something = "quiz has ended"
                        return render_template("studentlogin.html", data=d, student=student, something=something)
                # If Password is Wrong
                else:
                    return render_template("index.html", wrngPwd=True, uName=uName, pwd=pwd, quizId=quizId)
            # If Student is not invited to the particular Quiz
            else:
                return render_template("index.html", userNotFound=True, uName=uName, pwd=pwd, quizId=quizId)
        # If the Quiz does not Exist or Expire
        else:
            return render_template("index.html", invalidQuiz=True, uName=uName, pwd=pwd, quizId=quizId)


# Route to the Exam
@app.route("/startquiz", methods=["POST", "GET"])
def startquiz():
    global presentQuestion, totalQuestions, Questions, flag
    global teacher_Id, student_Id, quiz_Id, eTime
    uName = request.form.get("email")
    quizId = request.form.get("QuizId")
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return render_template("index.html", noNetword=True)
    cur = conn.cursor()
    cur.execute('''SELECT * FROM STUDENT WHERE QUIZ_ID='{}' AND EMAIL='{}' '''.format(quizId, uName))
    details = cur.fetchall()
    conn.commit()
    pwd = details[0][2]
    cur.execute('''SELECT * FROM QUIZ WHERE QUIZ_ID='{}' '''.format(quizId))
    d = cur.fetchall()
    conn.commit()
    conn.close()
    if int(flag) <= 2:
        pass
    else:
        return redirect("submitted")
    student_Id = uName
    data = d[0][3].split("T")
    startDate = data[0]
    startTime = data[1].split(":")
    startTime = (startTime[0] + startTime[1])
    endData = d[0][4].split("T")
    endDate = endData[0]
    endTime1 = endData[1]
    endTime = endData[1].split(":")
    endTime = (endTime[0] + endTime[1])
    message = "Quiz {} is Scheduled to start at {} {}\nIt will end at {} {}".format(quizId, data[0], data[1],
                                                                                    endData[0], endData[1])
    print(message)
    endTime = endData[0][5:7] + " " + endData[0][8:10] + ", " + endData[0][0:4] + " " + endData[1]
    print(endTime)
    eTime = endTime
    quiz_Id = quizId
    print("i came here")
    c1 = c2 = c3 = c4 = ""
    Questions = [[1, "Q1", "A", "B", "C", "D"],
                 [2, "Q2", "E", "F", "G", "H"],
                 [3, "Q3", "I", "J", "K", "L"]]
    totalQuestions = 2
    conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                           user="DARKKNIGHT",
                           passwd=PASSWORD, database="DBMSFLASKPROJECT")
    cur = conn.cursor()
    cur.execute('''SELECT Q_NO, QUESTION, OP_1, OP_2, OP_3, OP_4 FROM QUESTIONS WHERE QUIZ_ID='{}' '''.format(
        quizId))
    Questions = cur.fetchall()
    conn.commit()
    conn.close()
    conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                           user="DARKKNIGHT",
                           passwd=PASSWORD, database="DBMSFLASKPROJECT")
    cur = conn.cursor()
    cur.execute('''SELECT NO_OF_QUESTIONS FROM QUIZ WHERE QUIZ_ID = '{}' '''.format(quizId))
    totalQuestions = cur.fetchall()
    print(totalQuestions)
    totalQuestions = totalQuestions[0][0]
    presentQuestion = 0
    conn = sqlite3.connect("Answers.sqlite")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS ANSWERS(QUESTION_NUMBER TEXT, ANSWER TEXT)''')
    conn.commit()
    for i in range(0, totalQuestions):
        cur.execute('''SELECT * FROM ANSWERS WHERE QUESTION_NUMBER =?''', (i,))
        rows = cur.fetchall()
        if rows:
            continue
        cur.execute('''INSERT OR IGNORE INTO ANSWERS VALUES(?, ?)''', (i, None))
        conn.commit()
    conn.close()
    conn = sqlite3.connect("Answers.sqlite")
    cur = conn.cursor()
    cur.execute('''SELECT ANSWER FROM ANSWERS WHERE QUESTION_NUMBER=?''', (0,))
    ans = cur.fetchall()
    if ans:
        ans = ans[0][0]
    if ans == '1':
        c1 = "checked"
    elif ans == '2':
        c2 = "checked"
    elif ans == '3':
        c3 = "checked"
    elif ans == '4':
        c4 = "checked"
    return render_template("StudentHome.html", endTime=endTime, username=uName, Questions=Questions,
                           total=totalQuestions, qno=0,
                           Loop=[x for x in range(1, totalQuestions + 1)],
                           c1=c1, c2=c2, c3=c3, c4=c4)


# Signup Route--> To Create a Teacher Account
@app.route("/signup", methods=["GET", "POST"])
def singup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        # Getting the Details entered by the teacher
        emailId = request.form.get("emailId")
        fName = request.form.get("fName")
        lName = request.form.get("lName")
        mobile = request.form.get("mobile")
        subject = request.form.get("subject")
        institutionName = request.form.get("institutionName")
        signupPassword = request.form.get("signupPassword")
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
            cur = conn.cursor()
            cur.execute('''SELECT EMAIL FROM TEACHER WHERE EMAIL='{}' '''.format(emailId))
            users = cur.fetchall()
            # Checking if the user existence with same email
            if users:
                return render_template("signup.html", specialCharacter=False, emailId=emailId, fName=fName, lName=lName,
                                       mobile=mobile, subject=subject, institutionName=institutionName,
                                       signupPassword=signupPassword, userExists=True)
        except Exception as E:
            print(E)
            return render_template("signup.html", specialCharacter=False, emailId=emailId, fName=fName, lName=lName,
                                   mobile=mobile, subject=subject, institutionName=institutionName,
                                   signupPassword=signupPassword, noNetwork=True)
        # Checking the mobile Number they have entered
        try:
            mobile = int(mobile)
        except ValueError:
            print(emailId, fName, lName, mobile, subject, institutionName, signupPassword)
            return render_template("signup.html", valueOfMobile=False, emailId=emailId, fName=fName, lName=lName,
                                   mobile=mobile, subject=subject, institutionName=institutionName,
                                   signupPassword=signupPassword)
        # Checking the mobile number they have entered
        if (mobile % 1000000000) == mobile:
            return render_template("signup.html", invalidMobile=True, emailId=emailId, fName=fName, lName=lName,
                                   mobile=mobile, subject=subject, institutionName=institutionName,
                                   signupPassword=signupPassword)
        if "~" in signupPassword:
            return render_template("signup.html", invalidChar=True, emailId=emailId, fName=fName, lName=lName,
                                   mobile=mobile, subject=subject, institutionName=institutionName,
                                   signupPassword=signupPassword)
        # Checking the Password length
        if len(signupPassword) < 8:
            return render_template("signup.html", lengthOfPassword=False, emailId=emailId, fName=fName, lName=lName,
                                   mobile=mobile, subject=subject, institutionName=institutionName,
                                   signupPassword=signupPassword)
        # Checking for Numeric Character in the password
        count = 0
        for i in range(48, 58):
            if chr(i) in signupPassword:
                count += 1
        if count == 0:
            return render_template("signup.html", numericCharacter=False, emailId=emailId, fName=fName, lName=lName,
                                   mobile=mobile, subject=subject, institutionName=institutionName,
                                   signupPassword=signupPassword)
        # Checking for Uppercase Character in the password
        count = 0
        for i in range(65, 91):
            if chr(i) in signupPassword:
                count += 1
        if count == 0:
            return render_template("signup.html", upperCase=False, emailId=emailId, fName=fName, lName=lName,
                                   mobile=mobile, subject=subject, institutionName=institutionName,
                                   signupPassword=signupPassword)
        # Checking for Special Character int the Password
        count = 0
        for i in range(33, 48):
            if chr(i) in signupPassword:
                count += 1
        for i in range(58, 65):
            if chr(i) in signupPassword:
                count += 1
        for i in range(91, 97):
            if chr(i) in signupPassword:
                count += 1
        for i in range(123, 126):
            if chr(i) in signupPassword:
                count += 1
        if count == 0:
            return render_template("signup.html", specialCharacter=False, emailId=emailId, fName=fName, lName=lName,
                                   mobile=mobile, subject=subject, institutionName=institutionName,
                                   signupPassword=signupPassword)
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as E:
            print(E)
            return render_template("signup.html", emailId=emailId, fName=fName, lName=lName,
                                   mobile=mobile, subject=subject, institutionName=institutionName,
                                   signupPassword=signupPassword, noNetwork=True)
        # Inserting the user Details into the Database
        cur = conn.cursor()
        sql = '''INSERT INTO TEACHER VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}')'''.format(emailId, fName, lName,
                                                                                                mobile, subject,
                                                                                                institutionName,
                                                                                                signupPassword)
        cur.execute(sql)
        conn.commit()
        conn.close()
        # Sending mail to user with their login id and password
        mail = Mail(app)
        message = Message("You are registered Mr {}".format(fName),
                          recipients=[emailId],
                          body="Hello {} {}\nUsername : {}\nPassword : {}".format(fName, lName, emailId,
                                                                                  signupPassword))
        # To add attachment
        # with app.open_resource("hello.txt") as fp:
        #     message.attach("testos.py", 'application/octet-stream', fp.read())
        mail.send(message)
        return render_template("index.html", creationValue=True)


# Teacher Home Route
@app.route("/teacherHome", methods=["GET", "POST"])
def teacherHome():
    global teacherName
    return render_template("teacherHome.html", username=teacherName)


# Route to clear files created in local Database
@app.route("/clear")
def clear():
    global totalQuestions, teacher_Id, teacherName
    for ques in range(1, totalQuestions + 1):
        if os.path.exists("static/Pie_Question{}.png".format(ques)):
            os.remove("static/Pie_Question{}.png".format(ques))
    if os.path.exists("static/BarChartFrequencyOfMarksByStudents.png"):
        os.remove('static/BarChartFrequencyOfMarksByStudents.png')
    return redirect("/teacherHome")


# Route to create Quiz
@app.route("/CreateQuiz", methods=["GET", "POST"])
def createQuiz():
    global quiz_Id, teacher_Id, teacherName
    print("Hello", teacher_Id)
    if request.method == "GET":
        return render_template("TeacherCreateQuiz.html")
    else:
        # Checking whether the user have an Internet connection or not
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as E:
            print(E)
            return render_template("TeacherCreateQuiz.html", username=teacherName, noNetwork=True)
        cur = conn.cursor()
        # Generating a random unique Quiz id
        QuizId = ''
        while True:
            QuizId = CreateQuizId()
            cur.execute('''SELECT * FROM QUIZ WHERE QUIZ_ID='{}' '''.format(QuizId))
            quizes = cur.fetchall()
            if not quizes:
                break
        quiz_Id = QuizId
        # Getting the value from the user
        noOfQues = request.form.get("NoOfQuestions")
        startTime = request.form.get("startTime")
        print(startTime)
        endTime = request.form.get("endTime")
        print(endTime)
        cMarks = request.form.get("crctAns")
        wMarks = request.form.get("wrngAns")
        instructions = request.form.get("instructions")
        print(quiz_Id, noOfQues, startTime, endTime, cMarks, wMarks, instructions)
        # Inserting the Quiz Details into the Database
        cur.execute('''INSERT INTO QUIZ VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')'''
                    .format(teacher_Id, QuizId, noOfQues, startTime, endTime, instructions, cMarks, wMarks))
        conn.commit()
        conn.close()
        return render_template("teacherHome.html", quizId=QuizId, quizAdded=True, username=teacherName)


# Route to Modify the Quiz
@app.route("/modifyQuiz", methods=["POST"])
def modifyQuiz():
    global teacher_Id, teacherName
    # Checking whether the user having an internet Connection or not
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return render_template("modifyQuiz.html", username=teacherName, noNetwork=True)
    cur = conn.cursor()
    # Fetching all quiz's of the Teacher
    cur.execute('''SELECT QUIZ_ID FROM QUIZ WHERE TEACHER='{}' '''.format(teacher_Id))
    data = cur.fetchall()
    print(data)
    print(teacher_Id)
    conn.commit()
    conn.close()
    return render_template("modifyQuiz.html", data=data, username=teacherName)


# Route to add Questions into the particular quiz
@app.route("/add", methods=["POST"])
def addQuestion():
    global teacherName, teacher_Id
    # Getting the Details entered by the user
    quizId = request.form.get("QuizId")
    quesNo = request.form.get("QuestionNumber")
    ques = request.form.get("Question")
    op1 = request.form.get("Option1")
    op2 = request.form.get("Option2")
    op3 = request.form.get("Option3")
    op4 = request.form.get("Option4")
    crctAns = request.form.get("CorrectAnswer")
    # Correcting should be either 1 or 2 or 3 or 4
    if 1 <= int(crctAns) <= 4:
        pass
    else:
        return render_template("modifyQuiz.html", error=True)
    print(quizId)
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return render_template("modifyQuiz.html", noNetwork=True, username=teacherName)
    cur = conn.cursor()
    cur.execute('''SELECT NO_OF_QUESTIONS FROM QUIZ WHERE QUIZ_ID='{}' '''.format(quizId))
    totQuestions = cur.fetchall()[0][0]
    cur.execute('''SELECT COUNT(*) FROM QUESTIONS WHERE QUIZ_ID='{}' '''.format(quizId))
    questions = cur.fetchall()[0][0]
    # Checking if the questions exceeding the total no of questions or not
    if int(questions) >= int(totQuestions):
        return render_template("modifyQuiz.html", full=True, username=teacherName)
    # Inserting the Question into the Database
    cur.execute('''INSERT INTO QUESTIONS VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
    '''.format(quizId, quesNo, ques, op1, op2, op3, op4, crctAns))
    conn.commit()
    conn.close()
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return render_template("modifyQuiz.html", noNetwork=True, username=teacherName)
    cur = conn.cursor()
    # Fetching the Quiz id's of the user
    cur.execute('''SELECT QUIZ_ID FROM QUIZ WHERE TEACHER='{}' '''.format(teacher_Id))
    data = cur.fetchall()
    print(data)
    print(teacher_Id)
    conn.commit()
    conn.close()
    return render_template("modifyQuiz.html", questionAdded=True, data=data, username=teacherName)


# Route to update a Question
@app.route("/update", methods=["POST"])
def updateQuestion():
    global teacherName, teacher_Id
    # Getting the values entered by the user
    quizId = request.form.get("QuizId")
    quesNo = request.form.get("QuestionNumber")
    ques = request.form.get("Question")
    op1 = request.form.get("Option1")
    op2 = request.form.get("Option2")
    op3 = request.form.get("Option3")
    op4 = request.form.get("Option4")
    crctAns = request.form.get("CorrectAnswer")
    print(quizId)
    # Checking for stable internet connection and Connecting to the Database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return render_template("modifyQuiz.html", noNetwork=True, username=teacherName)
    cur = conn.cursor()
    # Updating the Question in the Database
    cur.execute('''UPDATE QUESTIONS SET QUESTION='{}', OP_1='{}', OP_2='{}', OP_3='{}', OP_4='{}', CRCT_ANS='{}' WHERE 
    QUIZ_ID='{}' AND Q_NO='{}' '''.format(ques, op1, op2, op3, op4, crctAns, quizId, quesNo))
    conn.commit()
    conn.close()
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return render_template("modifyQuiz.html", noNetwork=True, username=teacherName)
    cur = conn.cursor()
    # Fetching the Quiz id's of the particular user
    cur.execute('''SELECT QUIZ_ID FROM QUIZ WHERE TEACHER='{}' '''.format(teacher_Id))
    data = cur.fetchall()
    print(data)
    print(teacher_Id)
    # Closing the Database Connection
    conn.commit()
    conn.close()
    return render_template("modifyQuiz.html", questionUpdated=True, data=data, username=teacherName)


# Route to Delete A Question
@app.route("/delete", methods=["POST"])
def deleteQuestion():
    global teacherName, teacher_Id
    # Getting the Values Entered by the user
    quizId = request.form.get("QuizId")
    quesNo = request.form.get("QuestionNumber")
    # Checking for a stable internet Connection and connecting to the database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return render_template("modifyQuiz.html", noNetwork=True, username=teacherName)
    cur = conn.cursor()
    # Deleting the Question from the Database
    cur.execute('''DELETE FROM QUESTIONS WHERE QUIZ_ID='{}' AND Q_NO='{}' '''.format(quizId, quesNo))
    # Closing the Database Connection
    conn.commit()
    conn.close()
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return render_template("modifyQuiz.html", noNetwork=True, username=teacherName)
    cur = conn.cursor()
    cur.execute('''SELECT QUIZ_ID FROM QUIZ WHERE TEACHER='{}' '''.format(teacher_Id))
    data = cur.fetchall()
    print(data)
    print(teacher_Id)
    conn.commit()
    conn.close()
    return render_template("modifyQuiz.html", questionDeleted=True, data=data, username=teacherName)


# Route to Show all the Questions in the Quiz
@app.route("/showAll", methods=["POST"])
def showAllQuestion():
    global teacherName, teacher_Id
    # Getting the Quiz id entered by the user
    quizId = request.form.get("QuizId")
    # Checking for a stable connection and connecting to the database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    # If no Network
    except Exception as E:
        print(E)
        return render_template("showAll.html", noNetwork=True, username=teacherName)
    cur = conn.cursor()
    # Fetching the Questions from the Database
    cur.execute('''SELECT * FROM QUESTIONS WHERE QUIZ_ID='{}' '''.format(quizId))
    data = cur.fetchall()
    # Fetching the Column Names from the Database
    cur.execute('''SELECT `COLUMN_NAME` 
    FROM `INFORMATION_SCHEMA`.`COLUMNS` 
    WHERE `TABLE_SCHEMA`='DBMSFLASKPROJECT' 
        AND `TABLE_NAME`='QUESTIONS';''')
    cols = cur.fetchall()
    cols = (cols[7][0], cols[5][0], cols[6][0], cols[1][0], cols[2][0], cols[3][0], cols[4][0], cols[0][0])
    print(cols)
    conn.commit()
    conn.close()
    print(data)
    return render_template("showAll.html", data=data, cols=cols)


# Route to Invite the Students
@app.route("/inviteStudents", methods=["GET", "POST"])
def inviteStudents():
    global teacher_Id, quiz_Id, student_Id, teacherName
    teacher_Id = teacher_Id
    if request.method == "GET":
        # Checking for a stable internet connection and Connecting to the database
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                   user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        # If no Network
        except Exception as E:
            print(E)
            return redirect("/teacherHome")
        cur = conn.cursor()
        # Fetching the Quiz id's of that user
        cur.execute('''SELECT QUIZ_ID FROM QUIZ WHERE TEACHER='{}' '''.format(teacher_Id))
        data = cur.fetchall()
        print(data)
        conn.commit()
        conn.close()
        return render_template("studentInvite.html", data=data, username=teacher_Id)
    else:
        # Checking for a stable internet Connection and connecting to the Database
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                   user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as E:
            print(E)
            return redirect("/teacherHome")
        # Getting the Quiz Id entered by the User
        q_Id = request.form.get("QuizId")
        # Getting the File uploaded by the User
        file = request.files['file']
        # Saving the File in the current directory to access the data
        file.save(file.filename)
        print(file)
        print(file.filename)
        # Opening the file in read mode
        File = open(file.filename, "r")
        data = File.readlines()
        print(data)
        email = []
        name = []
        # Getting the email and names separated
        for line in data[1:]:
            line = line.split(",")
            email.append(line[0])
            name.append(line[1][:-1])
        print(email)
        print(name)
        for m, n in zip(email, name):
            pw = []
            # Generating a random Password for each student in the list
            for i in range(10):
                pw.append(chr(random.randint(33, 122)))
            password = ""
            for x in pw:
                password += x
            print(m)
            print(password)
            cur = conn.cursor()
            # Inserting Student Details into the Database
            cur.execute(''' INSERT INTO STUDENT VALUES('{}','{}','{}','{}', '{}', '{}') '''.format(m, n, password, q_Id,
                                                                                                   None, 0))
            conn.commit()
            mail = Mail(app)
            # Initializing message with the below details
            message = Message("You are registered as {}".format(n),
                              recipients=[m])
            try:
                conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                       user="DARKKNIGHT",
                                       passwd=PASSWORD, database="DBMSFLASKPROJECT")
            except Exception as E:
                print(E)
                return redirect("/teacherHome")
            # Getting the Details of the Quiz from the Database
            cur = conn.cursor()
            cur.execute('''SELECT START_TIME, END_TIME FROM QUIZ WHERE QUIZ_ID='{}' '''.format(q_Id))
            rows = cur.fetchall()
            startTime = rows[0][0]
            startTime = startTime.replace("T", " ")
            endTime = rows[0][1]
            endTime = endTime.replace("T", " ")
            if int(startTime[14:]) < 55:
                loginTime = startTime[:14] + str(int(startTime[14:]) + 5)
            else:
                loginTime = startTime[:11] + str(int(startTime[11:13]) + 1) + startTime[13:]
            print(loginTime)
            # Committing Changes to the Database
            conn.commit()
            # Adding Html to the mail
            message.html = render_template("mail.html", quizId=q_Id, teacher=teacher_Id, student=n, startTime=startTime,
                                           endTime=endTime, loginTime=loginTime, username=m, password=password)
            # Sending mail to the Student
            mail.send(message)
        # Closing Database Connection
        conn.close()
        return render_template("teacherHome.html", username=teacherName)


# Route to view Results
@app.route("/viewResults", methods=["GET", "POST"])
def view_results():
    global quiz_Id, teacher_Id, teacherName
    if request.method == "GET":
        # Checking for a stable connection and Connecting to the Database
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                   user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as E:
            print(E)
            return redirect("/teacherHome")
        cur = conn.cursor()
        # Fetching Quiz id's of that user
        cur.execute('''SELECT QUIZ_ID FROM QUIZ WHERE TEACHER='{}' '''.format(teacher_Id))
        data = cur.fetchall()
        print(data)
        return render_template("viewResults.html", username=teacherName, data=data)
    # Getting the Quiz id entered by the user
    quizId = request.form.get('QuizId')
    if quizId:
        quiz_Id = quizId
    # Checking for a stable internet connection and connecting to the database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                               user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    # If no network
    except Exception as E:
        print(E)
        return redirect("/teacherHome")
    cur = conn.cursor()
    # Fetching Student with their marks
    cur.execute('''SELECT NAME,MARKS, FLAG FROM STUDENT WHERE QUIZ_ID='{}' ORDER BY NAME'''.format(quiz_Id))
    results = cur.fetchall()
    return render_template('view_results.html', data=results, quiz_Id=quiz_Id)


# Route to Search a Particular Student in the results list
@app.route("/searchstudent", methods=["GET", "POST"])
def searchstudent():
    global quiz_Id
    if request.method == "POST" or 1:
        # Getting the student name of the student entered by the teacher
        student_results = request.form['searchstudent']
        print(quiz_Id)
        # Checking for a stable connection and connecting to the database
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                   user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as E:
            print(E)
            return redirect("/teacherHome")
        cur = conn.cursor()
        # Selecting that student from the Database
        cur.execute(
            '''SELECT NAME,MARKS, FLAG FROM STUDENT WHERE NAME LIKE '%{}%' AND QUIZ_ID='{}' '''.format(student_results,
                                                                                                       quiz_Id))
        # If No Such Student Exists then displaying all students
        results = cur.fetchall()
        if len(results) == 0 or student_results == 'all':
            # Checking for a stable connection and connecting to the Database
            try:
                conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                       user="DARKKNIGHT",
                                       passwd=PASSWORD, database="DBMSFLASKPROJECT")
            except Exception as E:
                print(E)
                return redirect("/teacherHome")
            cur = conn.cursor()
            # Selecting all Students from the Database
            cur.execute('''SELECT NAME,MARKS, FLAG FROM STUDENT WHERE QUIZ_ID='{}' '''.format(quiz_Id))
            results = cur.fetchall()
            return render_template('searchstudent.html', data=results, searched_student=student_results,
                                   quiz_Id=quiz_Id)
        return render_template('searchstudent.html', data=results, searched_student=student_results, quiz_Id=quiz_Id)


# Route to Download Results of a particular Quiz
@app.route("/download_data", methods=["GET", "POST"])
def download_data():
    global quiz_Id
    if request.method == "POST" or 1:
        conn = ''
        # Checking for a stable connection and connecting to the Database
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as e:
            print(e)
        cur = conn.cursor()
        print(quiz_Id[0])
        # Fetching the Student marks from the Database
        cur.execute('''SELECT NAME,MARKS, FLAG FROM STUDENT WHERE QUIZ_ID='{}' '''.format(quiz_Id))
        results = cur.fetchall()
        # Creating a file
        output = io.StringIO()
        # Writer to write data to the file
        writer = csv.writer(output)
        line = ['Student Name', 'Student Marks', 'FLAG']
        writer.writerow(line)
        # Writing Data of the Students into the file
        for row in results:
            line = [str(row[0]), row[1], row[2]]
            writer.writerow(line)
        output.seek(0)
        return Response(output, mimetype="text/csv",
                        headers={"content-Disposition": "attachment;filename=Quiz_{}_Results.csv".format(quiz_Id)})


# Route to view the Analysis
@app.route("/viewAnalysis", methods=["GET", "POST"])
def viewAnalysis():
    global teacher_Id, quiz_Id, teacherName
    if request.method == "GET":
        # Checking for a stable connection and connecting to the Database
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as E:
            print(E)
            return render_template("viewAnalysis.html", noNetwork=True, username=teacherName)
        cur = conn.cursor()
        # Fetching all Quiz id's of that user from Database
        cur.execute('''SELECT QUIZ_ID FROM QUIZ WHERE TEACHER='{}' '''.format(teacher_Id))
        data = cur.fetchall()
        print(data)
        # Committing and Closing the Database Connection
        conn.commit()
        conn.close()
        return render_template("viewAnalysis.html", data=data, username=teacherName)
    else:
        # Getting the Quiz id entered by the user
        quizId = request.form.get("QuizId")
        quiz_Id = quizId
        # Checking for a stable connection and connecting to the Database
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                   user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as E:
            print(E)
            return redirect("/teacherHome")
        cur = conn.cursor()
        # Fetching the no of students invited for the exam from Database
        cur.execute('''SELECT COUNT(*) FROM STUDENT WHERE QUIZ_ID='{}' '''.format(quizId))
        conn.commit()
        noOfStudentsInvited = cur.fetchall()[0][0]
        noOfStudentsAttempted = noOfStudentsSkipped = avgMark = aboveAvg = belowAvg = 0
        if noOfStudentsInvited != '0':
            # Fetching Students who have attempted the Exam
            cur.execute('''SELECT COUNT(*) FROM STUDENT WHERE QUIZ_ID='{}' AND MARKS != '{}' '''.format(quizId, None))
            conn.commit()
            noOfStudentsAttempted = cur.fetchall()[0][0]
            # SkippedStudents will be with marks None
            noOfStudentsSkipped = int(noOfStudentsInvited) - int(noOfStudentsAttempted)
            # Fetching the Avg marks of the Students
            cur.execute('''SELECT AVG(MARKS) FROM STUDENT WHERE QUIZ_ID='{}' AND MARKS != '{}' '''.format(quizId, None))
            conn.commit()
            avgMark = cur.fetchall()[0][0]
            # Selecting the no of students with marks above Average
            cur.execute(
                '''SELECT COUNT(*) FROM STUDENT WHERE QUIZ_ID='{}' AND MARKS >= '{}' AND MARKS !='None' '''.format(
                    quizId, avgMark))
            conn.commit()
            aboveAvg = cur.fetchall()[0][0]
            belowAvg = int(noOfStudentsAttempted) - int(aboveAvg)
        return render_template("overallAnalysis.html", noOfStudentsInvited=noOfStudentsInvited,
                               noOfStudentsAttempted=noOfStudentsAttempted, noOfStudentsSkipped=noOfStudentsSkipped,
                               avgMark=avgMark, aboveAvg=aboveAvg, belowAvg=belowAvg)


# Route To View Detailed Analysis
@app.route("/detailedAnalysis", methods=["GET", "POST"])
def detailedAnalysis():
    global quiz_Id, totalQuestions
    # Checking for a stable connection and connecting to the Database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                               user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return redirect("/teacherHome")
    cur = conn.cursor()
    slices = []
    sl = []
    # Selecting no of questions of that quiz from the database
    cur.execute('''SELECT NO_OF_QUESTIONS FROM QUIZ WHERE QUIZ_ID='{}' '''.format(quiz_Id))
    totQuestions = cur.fetchall()[0][0]
    totalQuestions = totQuestions
    # Selecting Students who answered question with option 1, option 2, option 3, option 4 for every question with quiz
    for q in range(0, totQuestions):
        for i in range(1, 5):
            cur.execute(
                '''SELECT COUNT(*) FROM ANSWERS WHERE QUIZ_ID='{}' AND ANSWER='{}' AND Q_NO='{}' '''.format(quiz_Id, i,
                                                                                                            q))
            answers = cur.fetchall()
            sl.append(answers[0][0])
        print(sl)
        slices.append(sl)
        sl = []
    print(slices)
    activities = ['Option1', 'Option2', 'Option3', 'Option4']
    colors = ['#0ac2ff', '#2ecc71', '#ff1255', '#f56342']
    # For every Question
    for s in slices:
        print(s)
    urls = []
    for s in slices:
        # Making a ie chart and saving in the static directory
        plt.pie(s, labels=activities, colors=colors,
                startangle=90, shadow=True, explode=(0, 0, 0.1, 0),
                radius=1.2, autopct='%1.1f%%')
        plt.legend()
        plt.savefig('static/Pie_Question{}.png'.format(slices.index(s)))
        # Checking for a stable connection and connecting to the database
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                   user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as E:
            print(E)
            return redirect("/teacherHome")
        cur = conn.cursor()
        # Selecting correcting answer of that question in that quiz from Database
        cur.execute(
            '''SELECT CRCT_ANS FROM QUESTIONS WHERE QUIZ_ID='{}' AND Q_NO='{}' '''.format(quiz_Id, slices.index(s)+1))
        cAns = cur.fetchall()
        correctlyAnswered = 0
        if cAns[0][0] == '1':
            correctlyAnswered = s[0]
        elif cAns[0][0] == '2':
            correctlyAnswered = s[1]
        elif cAns[0][0] == '3':
            correctlyAnswered = s[2]
        else:
            correctlyAnswered = s[3]
        # Appending the paths of pie chart in urls
        urls.append((slices.index(s), sum(s), correctlyAnswered, sum(s) - correctlyAnswered,
                     'static/Pie_Question{}.png'.format(slices.index(s))))
        plt.close()
    marks = []
    # Fetching Marks of Students of that Quiz from Database
    cur.execute(''' SELECT MARKS FROM STUDENT WHERE QUIZ_ID='{}' AND MARKS != 'None' '''.format(quiz_Id))
    lst = cur.fetchall()
    print(lst)
    for i in range(len(lst)):
        if lst[i][0] != "None":
            marks.append(int(lst[i][0]))
    marks.sort()
    if marks:
        # Calculating Mean, Mode and Median
        mean = statistics.mean(marks)
        mode = statistics.mode(marks)
        median = statistics.median(marks)
        print(mean, median, mode)
        # Maximum Marks = noOfQuestions * Marks for every Correct answer
        cur.execute(''' SELECT CMARKS*NO_OF_QUESTIONS FROM QUIZ WHERE QUIZ_ID='{}' '''.format(quiz_Id))
        maxMarks = int(cur.fetchall()[0][0])
        # Minimum Marks = noOfQuestions * Marks for every Wrong Answer
        cur.execute(''' SELECT WMARKS*NO_OF_QUESTIONS FROM QUIZ WHERE QUIZ_ID='{}' '''.format(quiz_Id))
        minMarks = int(cur.fetchall()[0][0])
        freq = []
        # Finding Frequency of Students with marks ranging from min marks to max marks
        for i in range(0, int(maxMarks) + 1):
            count = 0
            for x in marks:
                if int(i) == x:
                    count = count + 1
            if count != 0:
                freq.append(count)
        bar_x = []
        for i in marks:
            if i not in bar_x:
                bar_x.append(i)
        print(bar_x, "next is ", freq)
        tick_label = bar_x
        # Making Bar Chart
        plt.bar(bar_x, freq, tick_label=tick_label, width=1,
                color=['dodgerblue', '#2ecc71', '#ff1255', '#010fff', '#ff3456'])
        plt.xlabel('Marks')
        plt.ylabel('No of Students')
        plt.title('Marks Frequency')
        # Plotting Mean in Bar Chart
        plt.axvline(x=mean, ymin=minMarks, ymax=maxMarks, color='black', linestyle='--', label='Mean')
        # Plotting Median in Bar Chart
        plt.axvline(x=median, ymin=minMarks, ymax=maxMarks, color='black', linestyle='dotted', label='Median')
        # Plotting Mode in Bar Chart
        plt.axvline(x=mode, ymin=minMarks, ymax=maxMarks, color='black', linestyle='dashdot', label="Mode")
        plt.legend()
        # plt.show()
        # Saving the Bar Chart in the Static Directory
        plt.savefig('static/BarChartFrequencyOfMarksByStudents.png')
        # Closing the Plot
        plt.close()
        # Committing and Closing the Database Connection
        conn.commit()
        conn.close()
        return render_template("detailedAnalysis.html", urls=urls, bar='static/BarChartFrequencyOfMarksByStudents.png')
    return render_template("detailedAnalysis.html", urls=urls)


# Route To Delete Account
@app.route("/deleteAccount", methods=["GET", "POST"])
def deleteAccount():
    global teacher_Id, teacherName
    if request.method == 'GET':
        return render_template("deleteAccount.html")
    # Checking the User's response
    if request.form.get("select") == "yes":
        print("Inside if")
        # Checking for stable connection and connecting to the Database
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                   user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as E:
            print(E)
            return redirect("/teacherHome")
        cur = conn.cursor()
        # For Every Quiz id with that user we have to delete Quiz details, Questions, Students, Answers from the Database
        cur.execute('''SELECT QUIZ_ID FROM QUIZ WHERE TEACHER='{}' '''.format(teacher_Id))
        quizIds = cur.fetchall()
        print(quizIds)
        for item in quizIds:
            cur.execute('''DELETE  FROM QUIZ WHERE QUIZ_ID='{}' '''.format(item[0]))
            cur.execute('''DELETE  FROM QUESTIONS WHERE QUIZ_ID='{}' '''.format(item[0]))
            cur.execute('''DELETE  FROM ANSWERS WHERE QUIZ_ID='{}' '''.format(item[0]))
            cur.execute('''DELETE  FROM STUDENT WHERE QUIZ_ID='{}' '''.format(item[0]))
            conn.commit()
        cur.execute('''DELETE  FROM TEACHER WHERE EMAIL='{}' '''.format(teacher_Id))
        conn.commit()
        conn.close()

        return render_template("index.html", accountDeleted=True, username=teacherName)
    print("Redirected")
    return redirect("/teacherHome")


# Route to Student Home
@app.route("/studentHome", methods=["GET", "POST"])
def studentHome():
    print("Student Home")
    global flag
    flag += 1
    print(flag)
    return render_template("index.html")


# Route to go to next question
@app.route("/nxt", methods=["POST"])
def nxt():
    global presentQuestion, totalQuestions
    presentQuestion = presentQuestion
    print("Next is called")
    # Getting the response of the present question
    val = request.form.getlist("Options")
    print(val)
    conn = sqlite3.connect("Answers.sqlite")
    cur = conn.cursor()
    # Storing the response of the present question in the local Database
    if val:
        cur.execute('''UPDATE ANSWERS SET ANSWER=? WHERE QUESTION_NUMBER=?''', (val[0], presentQuestion))
    else:
        cur.execute('''UPDATE ANSWERS SET ANSWER=? WHERE QUESTION_NUMBER=?''', (None, presentQuestion))
    # Committing and Closing the Local Database Connection
    conn.commit()
    conn.close()
    c1 = c2 = c3 = c4 = ""
    # Checking if the Present Question is not the last Question
    if presentQuestion < totalQuestions - 1:
        presentQuestion += 1
    # Fetching the next Question answer from the database
    conn = sqlite3.connect("Answers.sqlite")
    cur = conn.cursor()
    cur.execute('''SELECT ANSWER FROM ANSWERS WHERE QUESTION_NUMBER=?''', (presentQuestion,))
    ans = cur.fetchall()
    if ans:
        ans = ans[0][0]
    if ans == '1':
        c1 = "checked"
    elif ans == '2':
        c2 = "checked"
    elif ans == '3':
        c3 = "checked"
    elif ans == '4':
        c4 = "checked"
    return render_template("studentHome.html", endTime=eTime, Questions=Questions, total=totalQuestions,
                           qno=presentQuestion,
                           Loop=[x for x in range(1, totalQuestions + 1)], c1=c1, c2=c2, c3=c3, c4=c4)


# Route to go to the previous Question
@app.route("/prev", methods=["POST"])
def prev():
    global presentQuestion, totalQuestions
    print("Prev is called")
    # Getting the Response of the present Question
    val = request.form.getlist("Options")
    print(val)
    conn = sqlite3.connect("Answers.sqlite")
    cur = conn.cursor()
    # Updating the Response of the present question in the Local Database
    if val:
        cur.execute('''UPDATE ANSWERS SET ANSWER=? WHERE QUESTION_NUMBER=?''', (val[0], presentQuestion))
    else:
        cur.execute('''UPDATE ANSWERS SET ANSWER=? WHERE QUESTION_NUMBER=?''', (None, presentQuestion))
    # Committing and Closing the Local Database Connection
    conn.commit()
    conn.close()
    c1 = c2 = c3 = c4 = ""
    # Checking the Present Question is not the first Question
    if presentQuestion > 0:
        presentQuestion = presentQuestion - 1
    conn = sqlite3.connect("Answers.sqlite")
    cur = conn.cursor()
    # Fetching the previous Question answer from the local Database
    cur.execute('''SELECT ANSWER FROM ANSWERS WHERE QUESTION_NUMBER=?''', (presentQuestion,))
    ans = cur.fetchall()
    if ans:
        ans = ans[0][0]
    if ans == '1':
        c1 = "checked"
    elif ans == '2':
        c2 = "checked"
    elif ans == '3':
        c3 = "checked"
    elif ans == '4':
        c4 = "checked"
    return render_template("studentHome.html", endTime=eTime, Questions=Questions, total=totalQuestions,
                           qno=presentQuestion,
                           Loop=[x for x in range(1, totalQuestions + 1)], c1=c1, c2=c2, c3=c3, c4=c4)


# Route to navigate between any Question
@app.route("/goto", methods=["POST"])
def goto():
    global presentQuestion, Questions, totalQuestions
    # Getting the Response of the present Question
    val = request.form.getlist("Options")
    print(val)
    conn = sqlite3.connect("Answers.sqlite")
    cur = conn.cursor()
    # Updating the Response of the present question in the Local Database
    if val:
        cur.execute('''UPDATE ANSWERS SET ANSWER=? WHERE QUESTION_NUMBER=?''', (val[0], presentQuestion))
    else:
        cur.execute('''UPDATE ANSWERS SET ANSWER=? WHERE QUESTION_NUMBER=?''', (None, presentQuestion))
    # Committing and Closing the Local Database Connection
    conn.commit()
    conn.close()
    # Getting the value of the question to which student wants to navigate
    btn = request.form.get("Navigate")
    presentQuestion = int(btn) - 1
    c1 = c2 = c3 = c4 = ""
    # Fetching the answer of that question from the Local Database
    conn = sqlite3.connect("Answers.sqlite")
    cur = conn.cursor()
    cur.execute('''SELECT ANSWER FROM ANSWERS WHERE QUESTION_NUMBER=?''', (presentQuestion,))
    ans = cur.fetchall()
    if ans:
        ans = ans[0][0]
    if ans == '1':
        c1 = "checked"
    elif ans == '2':
        c2 = "checked"
    elif ans == '3':
        c3 = "checked"
    elif ans == '4':
        c4 = "checked"
    return render_template("studentHome.html", endTime=eTime, Questions=Questions, total=totalQuestions,
                           qno=presentQuestion,
                           Loop=[x for x in range(1, totalQuestions + 1)], c1=c1, c2=c2, c3=c3, c4=c4)


# Route to Submit the Quiz
@app.route("/submitted", methods=["POST", "GET"])
def autoSubmit():
    global quiz_Id, student_Id, teacher_Id, flag
    global presentQuestion, totalQuestions, Questions
    val = request.form.getlist("Options")
    print(val)
    conn = sqlite3.connect("Answers.sqlite")
    cur = conn.cursor()
    # Updating the Response of the present question in the Local Database
    if val:
        cur.execute('''UPDATE ANSWERS SET ANSWER=? WHERE QUESTION_NUMBER=?''', (val[0], presentQuestion))
    else:
        cur.execute('''UPDATE ANSWERS SET ANSWER=? WHERE QUESTION_NUMBER=?''', (None, presentQuestion))
    # Committing and Closing the Local Database Connection
    conn.commit()
    conn.close()
    print("Submitted")
    # Checking for a stable connection and Connecting to the Database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                               user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return redirect("/studentHome")
    cur = conn.cursor()
    # Fetching the Quiz Data from the DataBase
    cur.execute('''SELECT NO_OF_QUESTIONS, START_TIME, END_TIME, CMARKS, WMARKS FROM QUIZ WHERE QUIZ_ID='{}' '''.format(
        quiz_Id))
    data = cur.fetchall()
    print(data)
    conn.commit()
    conn.close()
    # Selecting Answers which are not none from the Local Database
    conn = sqlite3.connect("Answers.sqlite")
    cur = conn.cursor()
    cur.execute('''SELECT * FROM ANSWERS WHERE ANSWER != ?''', ("",))
    answered = cur.fetchall()
    print(answered)

    noOfQuestionsAnswered = len(answered)
    # Checking for a stable connection and Connecting to the Database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                               user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return redirect("/teacherHome")
    cur = conn.cursor()
    # Fetching Correct Answers from the Database
    cur.execute('''SELECT Q_NO, CRCT_ANS FROM QUESTIONS WHERE QUIZ_ID='{}' '''.format(quiz_Id))
    answers = cur.fetchall()
    print(answers)
    a = []
    for answer in answers:
        a.append([int(answer[0]) - 1, answer[1]])
    print(a)
    noOfQuestionsAnsweredCorrectly = 0
    noOfQuestionsAnsweredWrongly = 0
    marks = 0
    # Fetching all Answers from the Local Database
    conn = sqlite3.connect("Answers.sqlite")
    cur = conn.cursor()
    cur.execute('''SELECT * FROM ANSWERS''')
    answered = cur.fetchall()
    print(answered)
    conn.commit()
    conn.close()
    # Calculating Marks by comparing Correct Answer with Student Answer
    for i, k in zip(answered, a):
        # Skipping if student didn't answer that question
        if i[1] is None:
            continue
        # If Student Answered Correctly
        if int(i[1]) == int(k[1]):
            noOfQuestionsAnsweredCorrectly += 1
            marks += int(data[0][3])
        # If Student Answered Wrongly
        else:
            noOfQuestionsAnsweredWrongly += 1
            marks += int(data[0][4])
    # Checking for Stable Connection and Connecting to the Database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185, user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
    cur = conn.cursor()
    # If Flag is 0 that means student didn't do any mal practice so flag will be S->No Mal Practice
    if flag == 0:
        cur.execute(
            '''UPDATE STUDENT SET MARKS='{}', FLAG='{}' WHERE QUIZ_ID='{}' AND EMAIL='{}' '''.format(marks, "S", quiz_Id,
                                                                                                     student_Id))
    # If Flag is not 0  that means student did mal practice so flag will be M->Malpractice
    else:
        cur.execute(
            '''UPDATE STUDENT SET MARKS='{}', FLAG='{}' WHERE QUIZ_ID='{}' AND EMAIL='{}' '''.format(marks, "M", quiz_Id,
                                                                                                     student_Id))
        flag = 0
    conn.commit()
    conn.close()
    # Checking for stable connection and Connecting to the Database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                               user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return redirect("/")
    cur = conn.cursor()
    # Inserting answers into the Student Table in the Database
    for i in answered:
        cur.execute('''INSERT INTO ANSWERS VALUES('{}', '{}', '{}', '{}')'''.format(quiz_Id, i[0], student_Id, i[1]))
        conn.commit()
    conn.close()
    return render_template("studentSubmit.html", totalQuestions=totalQuestions,
                           noOfQuestionsAnswered=noOfQuestionsAnswered,
                           noOfQuestionsAnsweredCorrectly=noOfQuestionsAnsweredCorrectly,
                           noOfQuestionsAnsweredWrongly=noOfQuestionsAnsweredWrongly,
                           noOfQuestionsSkipped=data[0][0] - noOfQuestionsAnswered,
                           marks=marks, cMarks=data[0][3], wMarks=data[0][4])


# Route to view the Response Sheet
@app.route("/download", methods=["POST", "GET"])
def download():
    global quiz_Id, student_Id
    print(quiz_Id)
    # Checking for stable connection and connecting to the Database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                               user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return redirect("/")
    cur = conn.cursor()
    # Fetching Quiz Details from the Database
    cur.execute('''SELECT NO_OF_QUESTIONS, START_TIME, END_TIME, CMARKS, WMARKS FROM QUIZ WHERE QUIZ_ID='{}' '''.format(
        quiz_Id))
    data = cur.fetchall()
    print(data)
    conn.commit()
    conn.close()
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                               user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return redirect("/")
    cur = conn.cursor()
    cur.execute('''SELECT * FROM ANSWERS WHERE ANSWER != '{}' AND QUIZ_ID='{}' AND STUDENT='{}' '''.format(None, quiz_Id, student_Id))
    answered = cur.fetchall()
    noOfQuestionsAnswered = len(answered)
    # Checking for Stable connection and Connecting to the Database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                               user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return redirect("/")
    cur = conn.cursor()
    # Fetching Correct Answers for all Questions from Database
    cur.execute('''SELECT Q_NO, CRCT_ANS FROM QUESTIONS WHERE QUIZ_ID='{}' '''.format(quiz_Id))
    answers = cur.fetchall()
    print(answers)
    a = []
    for answer in answers:
        a.append([int(answer[0]) - 1, answer[1]])
    # print(a)
    noOfQuestionsAnsweredCorrectly = 0
    noOfQuestionsAnsweredWrongly = 0
    marks = 0
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                               user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return redirect("/")
    cur = conn.cursor()
    cur.execute('''SELECT Q_NO, ANSWER FROM ANSWERS WHERE QUIZ_ID='{}' AND STUDENT='{}' '''.format(quiz_Id, student_Id))
    answered = cur.fetchall()
    conn.commit()
    conn.close()
    for i, k in zip(answered, a):
        if i[1] is None:
            continue
        if int(i[1]) == int(k[1]):
            noOfQuestionsAnsweredCorrectly += 1
            marks += int(data[0][3])
        else:
            noOfQuestionsAnsweredWrongly += 1
            marks += int(data[0][4])
    questions = []
    # Checking for stable Connection and connecting to the database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                               user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return redirect("/")
    cur = conn.cursor()
    # Fetching the Questions with options and Correct Answer from the Database
    cur.execute('''SELECT Q_NO, QUESTION, OP_1, OP_2, OP_3, OP_4, CRCT_ANS FROM QUESTIONS WHERE QUIZ_ID='{}' '''.format(
        quiz_Id))
    ques = cur.fetchall()
    z = []
    for q in ques:
        z.append([int(q[0]) - 1, q[1], q[2], q[3], q[4], q[5], q[6]])
    ques = z
    conn.commit()
    for q in ques:
        print(q)
        c1 = c2 = c3 = c4 = s1 = s2 = s3 = s4 = ""
        if int(q[6]) == 1:
            c1 = "dodgerblue"
        elif int(q[6]) == 2:
            c2 = "dodgerblue"
        elif int(q[6]) == 3:
            c3 = "dodgerblue"
        else:
            c4 = "dodgerblue"
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                   user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as E:
            print(E)
            return redirect("/")
        cur = conn.cursor()
        cur.execute('''SELECT ANSWER FROM ANSWERS WHERE Q_NO= '{}' AND QUIZ_ID='{}' AND STUDENT='{}' '''.format(
            q[0], quiz_Id, student_Id))
        sAns = cur.fetchall()
        print(sAns)
        conn.commit()
        conn.close()
        if sAns:
            if sAns[0][0] == '1':
                s1 = "#ff1255"
            elif sAns[0][0] == '2':
                s2 = "#ff1255"
            elif sAns[0][0] == '3':
                s3 = "#ff1255"
            elif sAns[0][0] == '4':
                s4 = "#ff1255"
        questions.append([int(q[0]) + 1, q[1], q[2], q[3], q[4], q[5], s1, s2, s3, s4, c1, c2, c3, c4])
    # os.remove("Answers.sqlite")
    return render_template("studentResponse.html", quizId=quiz_Id, startTime=data[0][1], endTime=data[0][2],
                           student=student_Id, noOfQuestions=data[0][0],
                           noOfQuestionsAnswered=noOfQuestionsAnswered,
                           noOfQuestionsAnsweredCorrectly=noOfQuestionsAnsweredCorrectly,
                           noOfQuestionsAnsweredWrongly=noOfQuestionsAnsweredWrongly,
                           noOfQuestionsSkipped=data[0][0] - noOfQuestionsAnswered, totalMarks=marks,
                           questions=questions)


# Route To forgot Password page
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    return render_template("emailotp.html")


# Route To Send Otp to the Email id of the user
@app.route("/sendotp", methods=["GET", "POST"])
def sendotp():
    global mail_id
    global random_number
    # Getting the mail id entered by the user
    mail_id = request.form.get("EMAIL")
    # Checking for stable connection and connecting to the Database
    try:
        conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                               user="DARKKNIGHT",
                               passwd=PASSWORD, database="DBMSFLASKPROJECT")
    except Exception as E:
        print(E)
        return redirect("/")
    cur = conn.cursor()
    # Fetching the user with that email id
    cur.execute('''SELECT EMAIL FROM TEACHER WHERE EMAIL='{}' '''.format(mail_id))
    email_ids = cur.fetchall()
    print(email_ids)
    conn.commit()
    conn.close()
    # If user Exists then sending OTP to their Email-Id
    if email_ids:
        # Generating a random number of length 4
        random_number = random.randint(1111, 9999)
        mail = Mail(app)
        # Sending mail to the user
        mail.send_message('OTP to change Password at Examination Portal', recipients=[mail_id],
                          body="OTP to change Password at Examination Portal is " + str(random_number))
        # Time is used to activate resend button in that page after 1 minute
        Time = datetime.now().strftime("%m %d, %Y %H:%M:%S")
        if Time[15:17] == '59':
            Time = Time[:15] + str(int(Time[15:17]) + 1) + Time[17:]
        else:
            Time = Time[:15] + str(int(Time[15:17]) + 1) + Time[17:]

        return render_template("otp.html", Time=Time)
    # If User is not found
    else:
        return render_template("emailotp.html", userNotFound=True, uName=mail_id)


# Route to Validate OTP
@app.route("/otpenter", methods=["GET", "POST"])
def enter_otp():
    global random_number
    # Getting the OTP entered by the User
    otp = request.form.get("OTP")
    print(otp)
    print(random_number)
    print(type(otp))
    print(type(random_number))
    # If Generated Otp and OTP entered by the user are same
    if int(otp) == random_number:
        return render_template("forgotpassword.html")
    # Invalid Otp
    else:
        return render_template("otp.html", invalidotp=True)


# Route to resend OTP
@app.route("/resend", methods=["GET", "POST"])
def reSendotp():
    global random_number
    # Generating a random number of length 4
    random_number = random.randint(1111, 9999)
    mail = Mail(app)
    # Sending Mail to the user
    mail.send_message('OTP to change Password at Examination Portal', recipients=[mail_id],
                      body="OTP to change Password at Examination Portal is " + str(random_number))
    # Time is used to activate resend button in that page
    Time = datetime.now().strftime("%m %d, %Y %H:%M:%S")
    if Time[15:17] == '59':
        Time = Time[:15] + str(int(Time[15:17]) + 1) + Time[17:]
    else:
        Time = Time[:15] + str(int(Time[15:17]) + 1) + Time[17:]
    return render_template("otp.html", Time=Time)


# Route to reset the Password
@app.route("/forgotPassword", methods=["GET", "POST"])
def reset_password():
    # Getting the password entered by the user
    password = request.form.get("Password")
    confirm_password = request.form.get("RPassword")
    # Checking for invalid characters in Password
    if "~" in password:
        return render_template("forgotpassword.html", invalidChar=True, password=password,
                               confirm_password=confirm_password)
    # Checking for Password Length
    if len(password) < 8:
        return render_template("forgotpassword.html", lengthOfPassword=False, password=password,
                               confirm_password=confirm_password)
    # Checking for Numeric Character in the Password
    count = 0
    for i in range(48, 58):
        if chr(i) in password and confirm_password:
            count += 1
    if count == 0:
        return render_template("forgotpassword.html", numericCharacter=False, password=password,
                               confirm_password=confirm_password)
    # Checking for Uppercase Character in the Password
    count = 0
    for i in range(65, 91):
        if chr(i) in password and confirm_password:
            count += 1
    if count == 0:
        return render_template("forgotpassword.html", upperCase=False, password=password,
                               confirm_password=confirm_password)
    # Checking for Special Character in the Password
    count = 0
    for i in range(33, 48):
        if chr(i) in password and confirm_password:
            count += 1
    for i in range(58, 65):
        if chr(i) in password and confirm_password:
            count += 1
    for i in range(91, 97):
        if chr(i) in password and confirm_password:
            count += 1
    for i in range(123, 126):
        if chr(i) in password and confirm_password:
            count += 1
    if count == 0:
        return render_template("forgotpassword.html", specialCharacter=False, password=password,
                               confirm_password=confirm_password)
    # Checking If password and re entered password are same
    if password == confirm_password:
        # Checking for stable connection and connecting to the Database
        try:
            conn = pymysql.connect(host="mysql-29185-0.cloudclusters.net", port=29185,
                                   user="DARKKNIGHT",
                                   passwd=PASSWORD, database="DBMSFLASKPROJECT")
        except Exception as E:
            print(E)
            return redirect("/")
        cur = conn.cursor()
        # Updating the Password in the Database
        cur.execute('''UPDATE TEACHER SET PASSWORD='{}' WHERE EMAIL='{}' '''.format(password, mail_id))
        # Committing and Closing the Connection
        conn.commit()
        conn.close()
        return render_template("index.html", PasswordUpdated=True)
    # If password and re-entered password are not same
    else:
        return render_template("forgotpassword.html", both_are_notsame=True, password=password,
                               confirm_password=confirm_password)


app.run()
