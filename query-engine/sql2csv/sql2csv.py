import csv
import sys
import simplejson as json
import cx_Oracle
import sqlparse

from flask import (
    Blueprint, Response, request, abort, current_app, make_response
)

bp = Blueprint('sql2csv', __name__, url_prefix='/')

class Line(object):
    def __init__(self):
        self._line = None
    def write(self, line):
        self._line = line
    def read(self):
        return self._line

def format_bytes(num):
    """Convert bytes to KB, MB, GB or TB"""
    step_unit = 1000.0 #1024 bad the size

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < step_unit:
            return "%3.1f %s" % (num, x)
        num /= step_unit

def lobOutConverter(value):
    """Return the LOB size instead of the LOB itself for display in UI"""
    lobsize = sys.getsizeof(value)
    lobsizeStr = format_bytes(lobsize)
    return f'LOB (size: {lobsizeStr})'

def OutputTypeHandler(cursor, name, defaultType, size, precision, scale):
    """Modify the fetched data types for LOB columns"""
    if defaultType == cx_Oracle.CLOB:
        return cursor.var(cx_Oracle.LONG_STRING, arraysize=cursor.arraysize, outconverter=lobOutConverter)
    if defaultType == cx_Oracle.BLOB:
        return cursor.var(cx_Oracle.LONG_BINARY, arraysize=cursor.arraysize, outconverter=lobOutConverter)

def iter_csv(data):
    """pipe_results helper function"""
    line = Line()
    writer = csv.writer(line)
    for csv_line in data:
        writer.writerow(csv_line)
        yield line.read()

def pipe_results(connection, cursor):
    """Loop through a SQL statement's result set and return as CSV"""
    if cursor is None:
        connection.close()
        return "Statement processed"
    line = Line()
    writer = csv.writer(line, delimiter=',', lineterminator="\n", quoting=csv.QUOTE_NONNUMERIC)
    try:
        for row in cursor:
            writer.writerow(row)
            yield line.read()
        cursor.close()
        connection.close()
    except cx_Oracle.DatabaseError as e:
        errorObj, = e.args
        print(errorObj.message)
        abort(400, description=errorObj.message)

def pipe_results_as_json(connection, cursor):
    """Loop through a SQL statement's result set and return as a JSON object"""
    if cursor is None:
        connection.close()
        return Response('{"message": "Statement processed"}', mimetype='application/json')
    def generate():
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        yield('{')
        yield(f'"columns":{json.dumps(columns)}, \n')
        yield('"rows": ')
        yield('[')
        try:
            firstRow = True
            for row in cursor:
                if firstRow:
                    firstRow = False
                    yield('\n')
                else:
                    yield (',\n')
                yield(json.dumps(row, default=str))
            cursor.close()
            connection.close()
            yield('\n]}')
        except cx_Oracle.DatabaseError as e:
            errorObj, = e.args
            print(errorObj.message)
            abort(400, description=errorObj.message)
    return Response(generate(), mimetype='application/json')

def get_connection(username, password, connectString):
    """Get an Oracle database connection"""
    try:
        connection = cx_Oracle.connect(username, password, connectString)
        connection.outputtypehandler = OutputTypeHandler
    except cx_Oracle.DatabaseError as e:
        errorObj, = e.args
        print(errorObj.message)
        abort(401, description=errorObj.message)
    else:
        return connection

def get_cursor(connection, sql, binds):
    """Create a cursor and execute a SQL statement"""
    try:
        cursor = connection.cursor()
        cursor.execute("set transaction read only")
        if binds == None:
            return cursor.execute(sql)
        else:
            return cursor.execute(sql, binds)
    except cx_Oracle.DatabaseError as e:
        errorObj, = e.args
        print(errorObj.message)
        abort(400, description=errorObj.message)

def get_connect_string(endpoint):
    """Get the connect string for a registered endpoint"""
    connectString = current_app.endpoints.get(endpoint)
    if connectString == None:
        return ''

    return connectString

@bp.route('/sql/<endpoint>', methods=['POST', 'GET'])
def sql2csv(endpoint):
    """Generate a CSV file or JSON object from a SQL statement

    POST a SQL statement + optional bind variables to a registered endpoint
    passing the database username and password as basic auth credentials.
    Returns a CSV stream or JSON object based on the value passed to the
    http Accept header.

    GET the connect string for a registered endpoint. Used by the UI to
    control access to the query functionality.
    """

    if request.method == 'POST':
        query = request.json
        user = request.authorization.username
        passwd = request.authorization.password
        connStr = get_connect_string(endpoint)
        httpHeaders = request.headers

        sql = query.get('sql')
        statements = list(sqlparse.parse(sql))
        for statement in statements:
            if statement.get_type() != 'SELECT':
                abort(403, description='SQL statement is not of type SELECT')

        connection = get_connection(user, passwd, connStr)
        cursor = get_cursor(connection, query.get('sql'), query.get('binds'))

        if httpHeaders.get('accept') == 'application/json':
            response = pipe_results_as_json(connection, cursor)
        else:
            response = Response(pipe_results(connection, cursor),
                                mimetype='text/csv')

        return response

    # return connect string or empty string for GET request
    response = make_response(get_connect_string(endpoint), 200)
    response.mimetype="text/plain"
    return response
