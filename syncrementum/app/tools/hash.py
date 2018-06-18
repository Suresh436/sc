__version__ = "1.3"
__all__ = ['PBKDF2', 'crypt']

from struct import pack
from random import randint
import string
import sys

try:
    # Use PyCrypto (if available).
    from Crypto.Hash import HMAC, SHA512 as SHA1
except ImportError:
    # PyCrypto not available.  Use the Python standard library.
    import hmac as HMAC
    try:
        from hashlib import sha512 as SHA1
    except ImportError:
        # hashlib not available.  Use the old sha module.
        import sha as SHA1

#
# Python 2.1 thru 3.2 compatibility
#

if sys.version_info[0] == 2:
    _0xffffffffL = long(1) << 32
    def isunicode(s):
        return isinstance(s, unicode)
    def isbytes(s):
        return isinstance(s, str)
    def isinteger(n):
        return isinstance(n, (int, long))
    def b(s):
        return s
    def binxor(a, b):
        return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a, b)])
    def b64encode(data, chars="+/"):
        tt = string.maketrans("+/", chars)
        return data.encode('base64').replace("\n", "").translate(tt)
    from binascii import b2a_hex
else:
    _0xffffffffL = 0xffffffff
    def isunicode(s):
        return isinstance(s, str)
    def isbytes(s):
        return isinstance(s, bytes)
    def isinteger(n):
        return isinstance(n, int)
    def callable(obj):
        return hasattr(obj, '__call__')
    def b(s):
       return s.encode("latin-1")
    def binxor(a, b):
        return bytes([x ^ y for (x, y) in zip(a, b)])
    from base64 import b64encode as _b64encode
    def b64encode(data, chars="+/"):
        if isunicode(chars):
            return _b64encode(data, chars.encode('utf-8')).decode('utf-8')
        else:
            return _b64encode(data, chars)
    from binascii import b2a_hex as _b2a_hex
    def b2a_hex(s):
        return _b2a_hex(s).decode('us-ascii')
    xrange = range

class PBKDF2(object):
    """PBKDF2.py : PKCS#5 v2.0 Password-Based Key Derivation"""

    def __init__(self, passphrase, salt, iterations=1000,
                 digestmodule=SHA1, macmodule=HMAC):
        self.__macmodule = macmodule
        self.__digestmodule = digestmodule
        self._setup(passphrase, salt, iterations, self._pseudorandom)

    def _pseudorandom(self, key, msg):
        """Pseudorandom function.  e.g. HMAC-SHA1"""
        return self.__macmodule.new(key=key, msg=msg,
            digestmod=self.__digestmodule).digest()

    def read(self, bytes):
        """Read the specified number of key bytes."""
        if self.closed:
            raise ValueError("file-like object is closed")

        size = len(self.__buf)
        blocks = [self.__buf]
        i = self.__blockNum
        while size < bytes:
            i += 1
            if i > _0xffffffffL or i < 1:
                # We could return "" here, but
                raise OverflowError("derived key too long")
            block = self.__f(i)
            blocks.append(block)
            size += len(block)
        buf = b("").join(blocks)
        retval = buf[:bytes]
        self.__buf = buf[bytes:]
        self.__blockNum = i
        return retval

    def __f(self, i):
        # i must fit within 32 bits
        assert 1 <= i <= _0xffffffffL
        U = self.__prf(self.__passphrase, self.__salt + pack("!L", i))
        result = U
        for j in xrange(2, 1+self.__iterations):
            U = self.__prf(self.__passphrase, U)
            result = binxor(result, U)
        return result

    def hexread(self, octets):
        """Read the specified number of octets. Return them as hexadecimal.

        Note that len(obj.hexread(n)) == 2*n.
        """
        return b2a_hex(self.read(octets))

    def _setup(self, passphrase, salt, iterations, prf):
        # Sanity checks:

        # passphrase and salt must be str or unicode (in the latter
        # case, we convert to UTF-8)
        if isunicode(passphrase):
            passphrase = passphrase.encode("UTF-8")
        elif not isbytes(passphrase):
            raise TypeError("passphrase must be str or unicode")
        if isunicode(salt):
            salt = salt.encode("UTF-8")
        elif not isbytes(salt):
            raise TypeError("salt must be str or unicode")

        # iterations must be an integer >= 1
        if not isinteger(iterations):
            raise TypeError("iterations must be an integer")
        if iterations < 1:
            raise ValueError("iterations must be at least 1")

        # prf must be callable
        if not callable(prf):
            raise TypeError("prf must be callable")

        self.__passphrase = passphrase
        self.__salt = salt
        self.__iterations = iterations
        self.__prf = prf
        self.__blockNum = 0
        self.__buf = b("")
        self.closed = False

    def close(self):
        """Close the stream."""
        if not self.closed:
            del self.__passphrase
            del self.__salt
            del self.__iterations
            del self.__prf
            del self.__blockNum
            del self.__buf
            self.closed = True

def crypt(word, salt=None, iterations=None):
    rawhash = PBKDF2(word, salt, iterations).read(24)
    return rawhash


