#import libraries
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request

app = Flask(__name__)

#Makes a connection to the database.
def getConn():
    
    conn = psycopg2.connect(database='coursework', user='postgres', password='password', host='localhost', port='5433')
    return conn

#Homepage.
@app.route('/')
def home():
    return render_template('home.html')

#Task1
@app.route('/task1', methods=['GET', 'POST'])
def task1():

    try:
        conn=None
        c_id = int(request.form['categoryid'])
        c_name = request.form['categoryname']
        c_type = request.form['categorytype']
            
        conn = getConn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('INSERT INTO bookstore.category(categoryid, name, categorytype) VALUES (%s, %s, %s)', [c_id, c_name, c_type])
        conn.commit()

        return render_template('home.html', msg1="Category added successfully.", error1="No error.")

    except Exception as e:
        return render_template('home.html', msg1="Category not added.", error1=e)

    finally:
        if conn:
            conn.close()
#Task2
@app.route('/task2', methods=['GET', 'POST'])
def task2():

    try:
        conn=None
        del_id = int(request.form['ciddelete'])

        conn = getConn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('DELETE FROM bookstore.category WHERE CategoryID = %s', [del_id])
        conn.commit()

        return render_template('home.html', msg2="Category deleted successfully.", error2="No error.")

    except Exception as e:
        return render_template('home.html', msg2="Category not deleted.", error2=e)

    finally:
        if conn:
            conn.close()

#Task3
@app.route('/task3', methods=['POST'])
def task3():

    try:
        conn=None

        conn = getConn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT name AS category, count(*) AS numberofbooksincategory, ROUND(AVG(price), 2) AS averagepriceofcategory \
                    FROM bookstore.category, bookstore.book \
                    WHERE category.categoryid = book.categoryid \
                    GROUP BY category.categoryid;')
        rows_main = cur.fetchall()
        
        cur.execute('SELECT COUNT(bookid) AS totalnumberofallbooks, ROUND( AVG(price), 2) AS averageallbookprice \
                    FROM bookstore.book')
        rows_summary = cur.fetchall()
        
        if rows_main:
            return render_template('task3.html', rows_main = rows_main, rows_summary=rows_summary)
        else:
            return render_template('home.html', msg3 = 'No data found.', error3="")

    except Exception as e:
        return render_template('home.html', msg3 = "Error occured.",  error3 = e)

    finally:
        if conn:
            conn.close()

#Task4
@app.route('/task4', methods=['POST'])
def task4():

    try:
        conn=None
        p_name = request.form['publishername']

        conn = getConn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT \
                    \
            TO_CHAR(orderdate, \'Mon\') AS month, \
            extract(year FROM orderdate) AS year, \
            orderline.bookid, title, COUNT(orderline.bookid) AS totalordersinmonth, \
            SUM(quantity) AS totalbooksorderedinmonth, \
            SUM(unitsellingprice * quantity) AS totalordervalueformonth, \
            SUM(price * quantity) AS totalretailvalueformonth\
                    \
            FROM bookstore.shoporder, bookstore.orderline, bookstore.book, bookstore.publisher \
            WHERE shoporder.shoporderid = orderline.shoporderid AND orderline.bookid = book.bookid AND book.publisherid = publisher.publisherid AND name = %s \
            GROUP BY TO_CHAR(orderdate, \'Mon\'), extract(year FROM orderdate), title, orderline.bookid \
            ORDER BY 1, 2', [p_name])

        rows_main = cur.fetchall()
        
        if rows_main:
            return render_template('task4.html', rows_main = rows_main)
        else:
            return render_template('home.html', msg4 = 'No data found.', error4="")

    except Exception as e:
        return render_template('home.html', msg4 = "Error occured.",  error4 = e)
    
    finally:
        if conn:
            conn.close()
#Task5

@app.route('/task5', methods=['POST'])
def task5():
    
    try:
        conn=None
        b_id = request.form['bookid']
        
        conn = getConn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT orderdate, title, price, unitsellingprice, quantity, (quantity * unitsellingprice) AS ordervalue, name as shopname \
            FROM bookstore.orderline, bookstore.shoporder, bookstore.shop, bookstore.book \
            WHERE orderline.shoporderid = shoporder.shoporderid AND shoporder.shopid = shop.shopid AND orderline.bookid = book.bookid AND book.bookid = %s \
            ORDER BY orderdate ASC', [b_id])
        
        rows_main = cur.fetchall()

        cur.execute('SELECT orderline.bookid, title, COUNT(orderline.bookid) AS numberoforders, SUM((quantity * unitsellingprice)) AS totalsellingvalue \
            FROM bookstore.orderline, bookstore.book \
            WHERE orderline.bookid = %s AND orderline.bookid = book.bookid \
            GROUP BY orderline.bookid, title', [b_id])

        rows_summary = cur.fetchall()

        if rows_main:
            return render_template('task5.html', rows_main = rows_main, rows_summary=rows_summary)
        else:
            return render_template('home.html', msg5 = 'No data found.', error5="")

    except Exception as e:
        return render_template('home.html', msg5 = "Error occured.",  error5 = e)

    finally:
        if conn:
            conn.close()
#Task6
@app.route('/task6', methods=['POST'])
def task6():

    try:
        conn=None
        start_date = request.form['startdate']
        end_date = request.form['enddate']

        conn = getConn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT name, SUM(quantity * unitsellingprice) AS totalsaleprice \
            FROM bookstore.orderline, bookstore.shoporder, bookstore.salesrep \
            WHERE shoporder.shoporderid = orderline.shoporderid AND shoporder.salesrepid = salesrep.salesrepid AND orderdate BETWEEN %s AND %s \
            GROUP BY name\
            ORDER BY totalsaleprice DESC', [start_date, end_date])

        rows_main = cur.fetchall()

        if rows_main:
            return render_template('task6.html', rows_main = rows_main)
        else:
            return render_template('home.html', msg6 = 'No data found.', error6="")
        
    except Exception as e:
        return render_template('home.html', msg6 = "Error occured.",  error6 = e)

    finally:
        if conn:
            conn.close()
            
#Task7
@app.route('/task7', methods=['GET', 'POST'])
def task7():

    try:
        conn=None
        percentdiscount = int(request.form['discountpercentage'])
        c_id = int(request.form['categoryid'])

        conn = getConn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('UPDATE bookstore.book SET price = (price * (%s * 0.01)) \
                    WHERE (SELECT categoryid FROM bookstore.category WHERE book.categoryid = category.categoryid) = %s', [percentdiscount, c_id])
        conn.commit()

        return render_template('home.html', msg7="Category discounted successfully.", error7="No error.")

    except Exception as e:
        return render_template('home.html', msg7="Category not discounted.", error7=e)

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug = True)



