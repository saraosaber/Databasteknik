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
        c.execute("DELETE FROM customer")
        db.commit()

        c.execute(
            """
            INSERT 
            INTO theater(name, capacity) 
            VALUES (?, ?), 
                   (?, ?), 
                   (?, ?)
            """, 
            ("Kino", 10, "Regal", 16, "Skandia", 100))
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
            (customer['username'], customer['fullName'], my_hash(customer['pwd']))
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
def my_hash(msg):
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
def post_performances():
    performance = request.json
    c = db.cursor()
    c.execute(
    """
    INSERT
    INTO screening(imdb_key, theater_name, date, start_time)
    VALUES (?,?,?,?)
    RETURNING screening_id
    """,
    [performance['imdbKey'], performance['theater'], performance['date'], performance['time']]
    )

    found = c.fetchone()
    if not found:
        response.status = 400
        return "No such movie or theater"
    else:
        db.commit()
        screening_id, = found
        c.execute(
            """
            UPDATE screening
            SET available_seats = (SELECT capacity
            FROM theater
            WHERE name = screening.theater_name)
            WHERE screening_id = ?
            """,
            [screening_id]
        )
        db.commit()
        response.status = 201


        return f"/performances/{screening_id}"




@get('/movies')
def get_movies():
    c = db.cursor()
    c.execute(
          """
          SELECT imdb_key, title, prod_year
          FROM movie
          """
    )
    found = c.fetchall()
    if not found:
        response.status = 400
        return "No movies found"
    else:
        response_data = [{"imdbKey": imdbKey,
                        "title": title,
                        "year": year} for imdbKey, title, year in found]
        response.status = 200
    return {"data": response_data}



@get('/movies/<imdb_key>')
def get_movies_with_ids(imdb_key):
    c = db.cursor()
    c.execute(
        """
        SELECT   imdb_key, title, prod_year
        FROM     movie
        WHERE    imdb_key = ?
        """,
        [imdb_key]
    )
    found = [{"imdbKey": imdbKey,
              "title": title,
              "year": year} for imdbKey, title, year in c]
    response.status = 200
    if len(found) == 0:
         response.status = 400
         return {"data": []}
    return {"data": found}

@get('/performances')
def get_performances():
    c = db.cursor()
    c.execute(
          """
          SELECT screening_id, date, start_time, title, prod_year, theater_name, available_seats
          FROM screening
          INNER JOIN movie using(imdb_key)
          INNER JOIN theater ON screening.theater_name == theater.name
          """
    )
    found = c.fetchall()
    if not found:
        response.status = 400
        return "No performances found"
    else:
        response_data = [{"performanceId": screeningId,
                          "date": date,
                          "startTime": startTime,
                          "title": title,
                          "year": year,
                          "theater": theater, 
                          "remainingSeats": remaining_seats} for screeningId, date, startTime, title, year, theater, remaining_seats in found]
        response.status = 200
    return {"data": response_data}



@post('/tickets')
def post_tickets():
    ticket = request.json
    c = db.cursor()
    c.execute(
        """
        SELECT available_seats
        FROM screening
        WHERE screening_id = ?
        """,
        [ticket['performanceId']]
    )
    found = c.fetchone()
    if not found:
        response.status = 400
        return "Performance not found"
    seats_before = found[0]
    c.execute(
        """
        SELECT password
        FROM customer
        WHERE username = ?
        """,
        [ticket['username']]
    )
    found = c.fetchone()
    if not found:
        response.status = 401
        return "Wrong user credentials"

    password = found[0]
    hashed_pwd = my_hash(ticket['pwd'])

    if seats_before > 0 and password == hashed_pwd:
        db.execute("begin")
        c.execute(
            """
            INSERT INTO ticket(username, screening_id)
            VALUES (?, ?)
            RETURNING ticket_id
            """,
            [ticket['username'], ticket['performanceId']]
        )
        ticket_id = c.fetchone()[0]
        c.execute(
            """
            UPDATE screening
            SET available_seats = available_seats - 1
            WHERE screening_id = ?
            """,
            [ticket['performanceId']]
        )
        db.commit()
        c.execute(
            """
            SELECT available_seats
            FROM screening
            WHERE screening_id = ?
            """,
            [ticket['performanceId']]
        )
        found = c.fetchone()
        seats_after = found[0]

        response.status = 201
        return f"/tickets/{ticket_id}"
    elif seats_before == 0:
        response.status = 400
        return "No tickets left"
    else:
        response.status = 401
        return "Wrong user credentials"



@get('/users/<username>/tickets')
def get_utickets(username):
    c = db.cursor()
    c.execute(
        """
        SELECT date, start_time, theater_name, title, prod_year, count() as nbrOfTickets
        FROM ticket
        JOIN screening USING  (screening_id)
        Join movie using (imdb_key)
        WHERE username = ?
        group by (screening_id)
        """,
        [username]
        )

    found = [{"date": date, "startTime": time, "theater": theater, "title": title, "year": year, "nbrOfTickets":nbrOfTickets}
         for (date, time, theater, title, year, nbrOfTickets) in c]
    response.status = 200
    return {"data": found}

run(host='localhost', port=PORT)