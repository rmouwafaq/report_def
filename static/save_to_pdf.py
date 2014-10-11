
import cgi; cgitb.enable();
import os
def index(req):

    # Create instance of FieldStorage
    form = cgi.FieldStorage()

    # Get data from fields
    dtbox = form.getvalue('dt')
    tmbox = form.getvalue('tm')


    req.write("voila")