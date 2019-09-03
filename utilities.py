from requests import get, post
from requests.exceptions import RequestException
from contextlib import closing
from re import sub
from os import mkdir, path


def session_post(url, session, payload):
    try:
        with closing(session.post(url, data=payload)) as resp:
                return resp
    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))



def session_get(url, session):
    try:
        resp = session.get(url, stream=True)
        session.close()
        return resp
        
    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        session.close()
        return None



def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))



def clean_file_name(name):
    # Remove apostrophes
    name = sub("\'", "", name)
    # Remove all other non-alpha/dash/underscore characters
    name = sub("[^\w\-\.]", "-", name)
    # Make lowercase
    name = name.lower()

    return name



def download_file(url, session, filename):
    if not path.exists(filename):
        resp = session_get(url, session)

        f = open(filename, "wb")
        f.write(resp.content)
        f.close()

