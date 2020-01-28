from models import Copyright


license = 'Copyright 2020 Paul Logston'


def insert_copyright(session):
    session.add(Copyright(
        text=license,
    ))
    session.flush()
