===================
python-livecodingtv
===================

This package wraps the Livecoding.tv REST API in Python.

Installation
------------

Using PIP::

  pip install python-livecodingtv

From Github::

  git clone ...
  cd python-livecodingtv
  python setup bdist 

More in information: https://docs.python.org/2/distutils/builtdist.html


Dependencies
------------

- requests
- bottle (examples)


Quick start guide
-----------------

Your application requires comunicate with the Livecoding.tv REST API. The 
livecodingtv.api.LctvOauth2App class encapsulate main logic of the OAuth2
authorization process and for the remote operations invocation. In summary 
the work flow is similar to this:

#. Create a LctvOauth2App object with your application credentials::

     app = LctvOauth2App(client_id, client_secret, redirect_uri, scope,grant_type)

#. Generate the authorization URL with your credentials::

     state,scope,auth_url = app.get_authorization_url()

#. ... a valid code is received as GET parameter in a request for
   REDIRECT_URI. the state is also a GET parameter of that request in order
   to link the code witht the original state. This part must be implemented
   by your application

#. Finally we can invoke any of the remote operations available::

     token = app.generate_token(code)
     operations = app.get_available_remote_api_calls()
     end_point = operations["/api/livestreams/"]["end_point"]
     token.api_operation_call(end_point,params)

Note that the app.get_available_remote_api_calls method discovers on the fly
the available methods provided by Livecoding.tv service.


Current available operations
----------------------------

The LctvOauth2Token delegates in the Livecoding.tv REST API the request and 
recovers the delivered information. The method for this is this::
    
    def LctvOauth2Token.api_operation_call(self,end_point,params={},always_refresh=False):
        ...

The :end_point is any of the available operations documented online
in https://www.livecoding.tv/developer/documentation/.

The :always_refresh forces the regeneration of the token anytime
that the API is used. This only is recommended in special cases
like debugging or similar stuffs.

The :params are any of the filter,ordering,searcing or similar
modifiers that Livecoding.tv supports::

        Searching:
            GET /api/user?search=russell

        Filter:
            GET /api/livestreams/?coding__name=python

        Ordering:
            GET /api/livestreams/?ordering=title
            GET /api/livestreams/?ordering=-title
            GET /api/scheduledbroadcast/?ordering=livestreams,title

        Format:
            GET /api/codingcategories/?format=api&offset=100
            GET /api/codingcategories/?format=json&offset=100

        Pagination:
            GET /api/codingcategories/?offset=100
            GET /api/codingcategories/?offset=200&limit=100


Recognized filters per API model
================================

CodingCategories::

    search = 'name','sort'
    ordering = 'name','sort'


LiveStream::

    filter = 'difficultylevel', 'channelstate', 'coding__name','language__name'
    search = 'title', 'description'
    ordering = 'title'


AccounLiveStream::

    scopes = "read:channel"
        

LiveStream::

    scopes = "read"


ScheduledBroadcast::

    filter = 'livestream', 'coding_category__name', 'coding_difficulty'
    search = 'title'
    ordering = 'start_time', 'livestream', 'title', 'id'


SiteLanguages::

    search = 'name'
    ordering = 'name'


UserView:

    search = 'username', 'slug'
    ordering = 'username', 'slug'


AccountUser::

    scopes =
       "read:viewer", # Provides access to a non crucial data of the user
       "read:user"  # Provides sensitive private data of the user (as the streaming_key)
    
    
Video::

    scopes = 'video'
    filter = 'difficultylevel', 'region', 'coding__name','language__name'
    search = 'title', 'description', 'slug'
    ordering = 'title','creation_time','slug'


XMPPAccount::

    scopes = "chat"



Bugs, comments and suggestions
------------------------------

Please, use the issue reporting track of Github to report this kind of
messages. All of them are welcome!.



