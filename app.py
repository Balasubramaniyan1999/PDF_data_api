from flask import Flask,redirect,render_template,url_for,request,session
from flask_mysqldb import MySQL
from os.path import join, dirname, realpath
import os
import PyPDF2
import re
from werkzeug.utils import secure_filename


app = Flask(__name__)

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/..')
ALLOWED_EXTENSIONS = set(['pdf'])

app.secret_key = 'data'

#database connection
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]="root"
app.config["MYSQL_DB"]="invoice"
app.config["MYSQL_CURSORCLASS"]="DictCursor"
mysql=MySQL(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')


#add data
@app.route('/adddata' , methods = ['POST'])
def adddata():
    input = request.files['file']
    if input and allowed_file(input.filename):
        filepath = secure_filename(input.filename)
        pdf_file = open(UPLOAD_FOLDER+'/'+filepath, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdf_file)
        pageObj = pdfReader.getPage(0)
        data = (pageObj.extractText())
        #Total section
        for data1 in data.splitlines():
            if 'TOTAL' in data1:
                p = re.compile(r'(?:Rs\.?|₹)\s*(\d+(?:[.,]\d+)*)|(\d+(?:[.,]\d+)*)\s*(?:Rs\.?|₹)')
                total = [x if x else y for x, y in p.findall(data1)]
                total_string = ''
                for x in total:
                    total_string = ''+ x
            else:
                message = 'Total was not found'
            
        #Date Section
        for data2 in data.splitlines():
            if 'Date' in data2:
                date_pattern = "\d{2}[/-]\d{2}[/-]\d{4}"
                date =  re.findall(date_pattern, data2)
                date_string = ''
                for y in date:
                    date_string = ''+ y
            else:
                message = 'Date was not found'

        pdf_file.close()
        con = mysql.connection.cursor()
        try:
            sql = "insert into data(doe,total) value (%s,%s)"
            con.execute(sql,[date_string,total_string])
            mysql.connection.commit()
            con.close()
            msg = "Data was saved in DB Successfully"
        except:
            msg = "Data was not save in DB"
    
    return render_template("home.html",content=msg)



if __name__ == '__main__':
    app.run()