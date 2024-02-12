from bottle import get, post, run, request, response
import sqlite3

PORT = 7007
db = sqlite3.connect('movies.sqlite')

@get('/ping')
def ping():
    response.status = 200
    return 'pong \n'


@post('/reset')
def reset():
    try:
        c = db.cursor()
        c.execute("DELETE FROM theater")
        c.execute("DELETE FROM screening")
        c.execute("DELETE FROM movie")
        c.execute("DELETE FROM ticket")
        c.execute("DELETE FROM movie")
        c.execute("DELETE FROM customer")
        db.commit()

        c.execute(
            """
            INSERT INTO theater(name, capacity) VALUES (?, ?)
            """, 
            ("Kino", 10))
        c.execute(
            """
            INSERT INTO theater(name, capacity) VALUES (?, ?)
            """, 
            ("Regal", 16))
        c.execute(
            """
            INSERT INTO theater(name, capacity) VALUES (?, ?)
            """, 
            ("Skandia", 100))
        db.commit()
        response.status = 201
        return "Database reset successfully."
    except sqlite3.Error as e:
        response.status = 500
        return f"An error occurred: {str(e)}"

@post('/users')
def post_users():
    customer = request.json
    c = db.cursor()
    try: 
        c.execute(
            """
            INSERT 
            INTO customer(username, full_name, password)
            VALUES(?,?,?)
            RETURNING username
            """,
            (customer['username'], customer['fullName'], hash(customer['pwd']))
        )
        found = c.fetchone()
        if not found:
            response.status = 400
            return "oh noo didnt work "
        else:
            db.commit()
            response.status = 201
            user = found
            return f"/users/{user[0]}"
    except sqlite3.IntegrityError:
            response.status = 409
            return "username already in use"      
def hash(msg):
    import hashlib
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()


@post('/movies')
def post_movies():
    movie = request.json
    c = db.cursor()
    try: 
        c.execute(
            """
            INSERT 
            INTO movie(IMDB_key, title, prod_year)
            VALUES(?,?,?)
            RETURNING IMDB_key
            """,
            (movie['imdbKey'], movie['title'], movie['year'])
        )
        found = c.fetchone()
        if not found:
            response.status = 400
            return "oh noo didnt work "
        else:
            db.commit()
            response.status = 201
            movie = found
            return f"/movies/{movie[0]}"
    except sqlite3.IntegrityError:
            response.status = 409
            return "imdbKey already in use"      

@post('/performances')
def post_movies():
    performance = request.json
    c = db.cursor()
    try: 
        c.execute(
            """
            INSERT 
            INTO screening(IMDB_key, theater_name, date, start_time)
            VALUES(?,?,?,?)
            RETURNING screening_id
            """,
            (performance['imdbKey'], performance['theater'], performance['date'], performance['time'])
        )
        found = c.fetchone()
        if not found:
            response.status = 400
            return "oh noo didnt work "
        else:
            db.commit()
            response.status = 201
            performance = found
            return f"/performances/{performance[0]}"
    except sqlite3.IntegrityError:
            response.status = 409
            return "imdbKey already in use" 



@get('/movies')
def get_movies():
    c = db.curson()
    c.execute(
          """
          SELECT imdb_key, title, year
          FROM movie
          """
    )
    found = c.fetchall()
    if not found:
        response.status = 400
        return "No movies found"
    response_data = [{"imdbKey": imdbKey,
                      "title": title,
                      "year": year} for imdbKey, title, year in found]
    response.status = 200
    return {"data": response_data}

run(host='localhost', port=PORT)
