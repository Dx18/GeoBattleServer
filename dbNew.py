from contextlib import closing
import sys


def newDb(db):
    with closing(db.getConn()) as dbConn:
        with dbConn.cursor() as cur:
            try:
                cur.execute(
                    """CREATE TABLE Players (
                        id SERIAL PRIMARY KEY,
                        name varchar(255),
                        password varchar(255),
                        token varchar(255),
                        email varchar(255),
                        r integer,
                        g integer,
                        b integer,
                        resources integer,
                        levelT integer,
                        levelG integer,
                        levelP integer,
                        activated integer,
                        tries integer
                        )
                        """)

                cur.execute(
                    """CREATE TABLE Sectors (
                        id SERIAL PRIMARY KEY,
                        x integer,
                        y integer,
                        idPlayer integer,
                        isBlocked integer
                        )
                        """)  # isBlocked is 0 or 1. 1==BLOCKED

                cur.execute(
                    """CREATE TABLE Buildings (
                        id SERIAL PRIMARY KEY,
                        x integer,
                        y integer,
                        type varchar(255),
                        idSector integer,
                        Data TEXT
                        )
                        """)

                cur.execute(
                    """CREATE TABLE Units (
                        id SERIAL PRIMARY KEY,
                        hangarId integer,
                        hangarSlot integer
                        )
                        """)

                cur.execute(
                    """CREATE TABLE Attacks (
                        id SERIAL PRIMARY KEY,
                        timeStop integer,
                        json TEXT,
                        myRuleJson TEXT
                        )
                        """)
                cur.execute(
                    """CREATE TABLE Updater (
                        id SERIAL PRIMARY KEY,
                        timeT integer,
                        json TEXT
                        )
                        """)
            except Exception as exc:
                print(exc)
                print('Error on line {}'.format(
                    sys.exc_info()[-1].tb_lineno))
