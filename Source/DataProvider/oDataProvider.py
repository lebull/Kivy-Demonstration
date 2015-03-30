from dataprovider import NetworkDataProvider


class ODataProvider(NetworkDataProvider):
    """
    ODataProvider interfaces with a remote oData service.  Data from requests
    are returned as an Entity or a set of Entities.
    """

    #TODO: This is a misnomer. It's more of a test of authentication credentials.
    def connect(self, url, username, password, on_success = None, on_failure = None):
        """
        Provides the kivy service with the target URL as well as credentials for
        basic authentication.  This also verifies that the username and password are
        valid credentials by attempting to pull the metadata from the target SAP
        gateway service.
        """
        self.setBasicAuth(username, password)
        self.url = url

        self.query(
            path = '$metadata',
            method = 'GET',
            on_success = on_success,
            on_failure = on_failure)

    def query(self, path, method = 'GET', on_success = None, on_failure = None):
        """Defines basic behavior on getEntity or getEntitySet."""

        #If we need need to parse our result...
        we_should_return_entities = method in ['GET']

        #Parse entities out of the result.  Call the callback with these results as params.
        #This should be called even if no callback is provided and the request is blocking.
        def on_success_local(request, result):
            if on_success != None:
                if we_should_return_entities:
                    #TODO: What are we doing with the parser?
                    #on_success(parser(result))
                    on_success(result)
                else:
                    on_success(result)

        #The default behavior if a request fails.
        def on_fail_local(request, result):
            #TODO: May not always have a response.  It may fail from no connection.

            if on_failure != None:
                on_failure(request.resp_status)

        self._sendRequest(
            path = path,
            method = method,
            on_success = on_success_local,
            on_failure = on_fail_local)

class ODataParser(object):
    """ HTTP Response goes in, Entity goes out """
    @classmethod
    def parseEntity(cls):
        """Parse a single entity"""
        pass
    
    @classmethod
    def parseEntities(cls):
        """Parse many entities"""
        pass
