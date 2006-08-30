# This code is in the public domain, it comes
# with absolutely no warranty and you can do
# absolutely whatever you want with it.

__date__ = '1 May 2006'
__version__ = '1.4'
__doc__= """
This is markup.py - a Python module that attempts to
make it easier to generate HTML/XML from a Python program
in an intuitive, lightweight, customizable and pythonic way.

The code is in the public domain.

Current version is %s as of %s.

Documentation and further info is at http://markup.sourceforge.net/

Please send bug reports, feature requests, enhancement
ideas or questions to nogradi at gmail dot com.

Installation: drop markup.py somewhere into your Python path
for example /usr/lib/pythonX.Y/site-packages with X.Y your
Python version.
""" % ( __version__, __date__ )

import string

class tag:
    """This class handles the addition of a new element (maybe should be called element and not tag :))."""

    def __init__( self, parent, tag ):
        self.parent = parent

	if self.parent.case == 'lower':
	    self.tag = tag.lower( )
	else:
	    self.tag = tag.upper( )
    
    def __call__( self, *args, **kwargs ):
        if len( args ) > 1:
            raise ArgumentError( self.tag )
        
        if self.tag in self.parent.twotags:
            for myarg, mydict in self.argsdicts( args, kwargs ):
                self.render( self.tag, False, myarg, mydict )
        
        elif self.tag in self.parent.onetags:
            if len( args ) == 0:
                for myarg, mydict in self.argsdicts( args, kwargs ):
                    # here myarg is always None, because len( args ) = 0
                    self.render( self.tag, True, myarg, mydict )
            else:
                raise ClosingError( self.tag )
        elif self.parent.mode == 'strict_html' and self.tag in self.parent.deptags:
            raise DeprecationError( self.tag )
        else:
            raise InvalidElementError( self.tag, self.parent.mode )
    
    def render( self, tag, single, between, kwargs ):
        """Append the actual tags to content."""

	out = "<%s" % tag
	for key, value in kwargs.iteritems():
            # strip this so class_ will mean class, etc.
            key = key.strip('_')
            # special cases, maybe change _ to - overall?
            if key == 'http_equiv':
                key = 'http-equiv'
            elif key == 'accept_charset':
                key = 'accept-charset'
            out = out + " %s='%s'" % ( key, value )
	if between is not None:
            between = str( between )
	    out = out + ">%s</%s>" % ( between, tag )
	else:
	    if single:
		out = out + " />"
	    else:
		out = out + ">"
	self.parent.content.append( out )	
    
    def close( self ):
        """Append a closing tag unless element has only opening tag."""

        if self.tag in self.parent.twotags:
            self.parent.content.append( "</%s>" % self.tag )
        elif self.tag in self.parent.onetags:
            raise ClosingError( self.tag )
        elif self.parent.mode == 'strict_html' and self.tag in self.parent.deptags:
            raise DeprecationError( self.tag )

    def open( self, **kwargs ):
        """Append an opening tag."""

        if self.tag in self.parent.twotags or self.tag in self.parent.onetags:
            self.render( self.tag, False, None, kwargs )
        elif self.mode == 'strict_html' and self.tag in self.parent.deptags:
            raise DeprecationError( self.tag )

    def argsdicts( self, args, mydict ):
        """A utility function, should not be used from outside."""

        # remove None values
        newdict = mydict.copy()
        for rem in mydict:
            if newdict[rem] == None:
                del newdict[rem]
        mydict=newdict.copy()

        # This will only be called with len( args ) = 0,1
        if len( args ) == 0:
            args = [ None ]
        elif len( args ) == 1:
            if isinstance( args[0], basestring ):
                args = [ args[0] ]
            else:
                args = list( args[0] )
        else:
            raise Exception, "We should have never gotten here."

        for key, value in mydict.iteritems( ):
            if isinstance( value, basestring ) or isinstance( value, int ):
                mydict[ key ] = [ value ]
            else:
                mydict[ key ] = list( value )
      
        lists = mydict.values( )
        lists.append( args )
        maxy = max( map( len, lists ) )

        argdict = [ ]
        for i in range( maxy ):
            thisdict = { }
            for key in mydict.keys( ):
                try:
                    thisdict[ key ] = mydict[ key ][ i ]
                except IndexError:
                    thisdict[ key ] = mydict[ key ][ -1 ]
            try:
                thisarg = args[ i ]
            except:
                thisarg = args[ -1 ]
            argdict.append( ( thisarg, thisdict ) )

        return argdict

        
class page:
    """This is our main class representing a document. Elements are added
    as attributes of an instance of this class."""

    def __init__( self, mode='strict_html', case='lower', onetags=None, twotags=None ):
        """Stuff that effects the whole document.

        mode -- 'strict_html'   for HTML 4.01
                'html'          alias for 'strict_html'
                'loose_html'    to allow some deprecated elements
                'xml'           to allow arbitrary elements

        case -- 'lower'         element names will be printed in lower case
                'upper'         they will be printed in upper case

        onetags --              list or tuple of valid elements with opening tags only
        twotags --              list or tuple of valid elements with both opening and closing tags
                                these two keyword arguments may be used to select
                                the set of valid elements in 'xml' mode
                                invalid elements will raise appropriate exceptions"""
        
        valid_onetags = [ "AREA", "BASE", "BR", "COL", "FRAME", "HR", "IMG", "INPUT", "LINK", "META", "PARAM" ]
        valid_twotags = [ "A", "ABBR", "ACRONYM", "ADDRESS", "B", "BDO", "BIG", "BLOCKQUOTE", "BODY", "BUTTON",
                "CAPTION", "CITE", "CODE", "COLGROUP", "DD", "DEL", "DFN", "DIV", "DL", "DT", "EM", "FIELDSET",
                "FORM", "FRAMESET", "H1", "H2", "H3", "H4", "H5", "H6", "HEAD", "HTML", "I", "IFRAME", "INS",
                "KBD", "LABEL", "LEGEND", "LI", "MAP", "NOFRAMES", "NOSCRIPT", "OBJECT", "OL", "OPTGROUP",
                "OPTION", "P", "PRE", "Q", "SAMP", "SCRIPT", "SELECT", "SMALL", "SPAN", "STRONG", "STYLE",
                "SUB", "SUP", "TABLE", "TBODY", "TD", "TEXTAREA", "TFOOT", "TH", "THEAD", "TITLE", "TR",
                "TT", "UL", "VAR" ]
        deprecated_onetags = [ "BASEFONT", "ISINDEX" ]
        deprecated_twotags = [ "APPLET", "CENTER", "DIR", "FONT", "MENU", "S", "STRIKE", "U" ]

        self.header = [ ]
	self.content = [ ]
        self.footer = [ ]
	self.case = case

        # init( ) sets it to True so we know that </body></html> has to be printed at the end
        self.full = False

	if mode == 'strict_html' or mode == 'html':
	    self.onetags = valid_onetags
	    self.onetags += map( string.lower, self.onetags )
	    self.twotags = valid_twotags
	    self.twotags += map( string.lower, self.twotags )
	    self.deptags = deprecated_onetags + deprecated_twotags
	    self.deptags += map( string.lower, self.deptags )
	    self.mode = 'strict_html'
	elif mode == 'loose_html':
	    self.onetags = valid_onetags + deprecated_onetags 
	    self.onetags += map( string.lower, self.onetags )
	    self.twotags = valid_twotags + deprecated_twotags
	    self.twotags += map( string.lower, self.twotags )
	    self.mode = mode
	elif mode == 'xml':
            if onetags and twotags:
                self.onetags = onetags
                self.twotags = twotags
            elif ( onetags and not twotags ) or ( twotags and not onetags ):
                raise CustomizationError( )
            else:
                self.onetags = russell( )
                self.twotags = russell( )
            self.mode = mode
	else:
	    raise ModeError( mode )

    def __getattr__( self, attr ):
        return tag( self, attr )

    def __str__( self ):
	str = ''
	for line in self.header + self.content + self.footer:
	    str = str + line + '\n'
        if self.full and ( self.mode == 'strict_html' or self.mode == 'loose_html' ):
            str = str + '</body>\n</html>'
	return str

    def __call__( self, escape=False ):
        """Return the document as a string.

        escape --   False   print normally
                    True    replace < and > by &lt; and &gt;
                            the default escape sequences in most browsers"""

        if escape:
            return _escape( self.__str__( ) )
        else:
            return self.__str__()

    def add( self, text ):
        """This is an alias to addcontent."""
        self.addcontent( text )

    def addfooter( self, text ):
        """Add some text to the bottom of the document"""
        self.footer.append( text )

    def addheader( self, text ):
        """Add some text to the top of the document"""
        self.header.append( text )

    def addcontent( self, text ):
        """Add some text to the main part of the document"""
        self.content.append( text )


    def init( self, lang='en', css=None, metainfo=None, title=None, header=None,
              footer=None, charset=None, encoding=None, doctype=None ):
        """This method is used for complete documents with appropriate
        doctype, encoding, title, etc information. For an HTML/XML snippet
        omit this method.

        lang --     language, usually a two character string, will appear
                    as <html lang='en'> in html mode (ignored in xml mode)
        
        css --      Cascading Style Sheet filename as a string or a list of
                    strings for multiple css files (ignored in xml mode)

        metainfo -- a dictionary in the form { 'name':'content' } to be inserted
                    into meta element(s) as <meta name='name' content='content'>
                    (ignored in xml mode)

        title --    the title of the document as a string to be inserted into
                    a title element as <title>my title</title> (ignored in xml mode)

        header --   some text to be inserted right after the <body> element
                    (ignored in xml mode)

        footer --   some text to be inserted right before the </body> element
                    (ignored in xml mode)

        charset --  a string defining the character set, will be inserted into a
                    <meta http-equiv='Content-Type' content='text/html; charset=myset'>
                    element (ignored in xml mode)

        encoding -- a string defining the encoding, will be put into to first line of
                    the document as <?xml version='1.0' encoding='myencoding' ?> in
                    xml mode (ignored in html mode)

        doctype --  the document type string, defaults to
                    <!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN'>
                    in html mode (ignored in xml mode)"""

        self.full = True

        if self.mode == 'strict_html' or self.mode == 'loose_html':
            if doctype is None:
                doctype = "<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN'>"
            self.header.append( doctype )
            self.html( lang=lang )
            self.head()
            if charset is not None:
                self.meta( http_equiv='Content-Type', content="text/html; charset=%s" % charset )
            if metainfo is not None:
                self.metainfo( metainfo )
            if css is not None:
                self.css( css )
            if title is not None:
                self.title( title )
            self.head.close()
            self.body()
            if header is not None:
                self.content.append( header )
            if footer is not None:
                self.footer.append( footer )

        elif self.mode == 'xml':
            if doctype is None:
                if encoding is not None:
                    doctype = "<?xml version='1.0' encoding='%s' ?>" % encoding
                else:
                    doctype = "<?xml version='1.0' ?>"
            self.header.append( doctype )

    def css( self, filelist ):
        """This convenience function is only useful for html.
        It adds css stylesheet(s) to the document via the <link> element."""
      
        if isinstance( filelist, basestring ):
            self.link( href=filelist, rel='stylesheet', type='text/css', media='all' )
        else:
            for file in filelist:
                self.link( href=file, rel='stylesheet', type='text/css', media='all' )

    def metainfo( self, mydict ):
        """This convenience function is only useful for html.
        It adds meta information via the <meta> element, the argument is
        a dictionary of the form { 'name':'content' }."""

        if isinstance( mydict, dict ):
            for name, content in mydict.iteritems( ):
                self.meta( name=name, content=content )
        else:
            raise TypeError, "Metainfo should be called with a dictionary argument of name:content pairs."

    def aimg( self, href='', src='', width=None, height=None, alt='This is an image.', aklass=None, imgklass=None, border=None ):
	"""Shorthand for <a ... ><img ... ></a>."""

        i = page( )
        i.img( src=src, width=width, height=height, alt=alt, class_=imgklass, border=border )
        simg =  str(i).replace("\n", "")
        self.a( simg, href=href ,class_=aklass )
 
def escape( text ):
    """Substitute &gt; for > and &lt; for < in text. Useful for rendering < or > in web browsers."""

    text = text.replace( '>', '&gt;' )
    text = text.replace( '<', '&lt;' )

    return text

_escape = escape

class russell:
    """A dummy class that contains anything."""

    def __contains__( self, item ):
	return True


class MarkupError( Exception ):
    """All our exceptions subclass this."""
    def __str__( self ):
	return self.message

class ClosingError( MarkupError ):
    def __init__( self, tag ):
	self.message = "The element '%s' does not accept non-keyword arguments (has no closing tag)." % tag

class OpeningError( MarkupError ):
    def __init__( self, tag ):
	self.message = "The element '%s' can not be opened." % tag

class ArgumentError( MarkupError ):
    def __init__( self, tag ):
	self.message = "The element '%s' was called with more than one non-keyword argument." % tag

class InvalidElementError( MarkupError ):
    def __init__( self, tag, mode ):
	self.message = "The element '%s' is not valid for your mode '%s'." % ( tag, mode )

class DeprecationError( MarkupError ):
    def __init__( self, tag ):
	self.message = "The element '%s' is deprecated, instantiate markup.page with mode='loose_html' to allow it." % tag

class ModeError( MarkupError ):
    def __init__( self, mode ):
	self.message = "Mode '%s' is invalid, possible values: strict_html, loose_html, xml." % mode

class CustomizationError( MarkupError ):
    def __init__( self ):
        self.message = "If you customize the allowed elements, you must define both types 'onetags' and 'twotags'."

if __name__ == '__main__':
    print __doc__
