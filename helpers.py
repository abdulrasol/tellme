UPLOAD_DIR = 'static/uploads'
USER_PROFILE_PIC = 'static/uploads/users'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d