#coding=utf8
__all__ = ['encrypt', 'decrypt', 'uencrypt', 'udecrypt']

from Crypto.Cipher import AES
from base64 import b64encode, b64decode
import time

secret = '\xce\xa2\xce\xa2\xba\xec\xd4\xe6\xc9\xcc\xb3'+'19312'
# the block size for the cipher object; must be 16 per FIPS-197
BLOCK_SIZE = 16

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# create a cipher object using the random secret
cipher = AES.new(secret)
c_encrypt = cipher.encrypt
c_decrypt = cipher.decrypt


def encrypt(s):
    return b64encode(c_encrypt(pad(s)))

def decrypt(s):
    return c_decrypt(b64decode(s)).rstrip(PADDING)

def uencrypt(s):
    return b64encode(c_encrypt(pad(s.encode('utf8') if type(s) is unicode else s)))

def udecrypt(s):
    return c_decrypt(b64decode(s)).rstrip(PADDING).decode('utf8')

if __name__ == '__main__':
    # n = time.time()
    # for i in range(10000):
    #     encoded = encrypt(u'翻译此页加解密'.encode('utf8'))
    #     #print 'Encrypted string:', encoded, len(encoded)
    #     decoded = decrypt(encoded)
    #     #print 'Decrypted string:', decoded
    # print '10000times encrypt & decrypt time: ', time.time() - n

    encoded = encrypt(u'翻译此页加解密'.encode('utf8'))
    print 'Encrypted string:', encoded, len(encoded)
    decoded = decrypt(encoded)
    print 'Decrypted string:', decoded, type(decoded), decoded.decode('utf8')
    print '------------uencrypt'
    encoded = uencrypt(u'翻译此页加解密')
    print 'Encrypted string:', encoded, len(encoded)
    decoded = udecrypt(encoded)
    print 'Decrypted string:', decoded, type(decoded)
    print '------------id_number'
    encoded = encrypt(u'4509231987021621221213'.encode('utf8'))
    print 'Encrypted string:', encoded, len(encoded)
    decoded = decrypt(encoded)
    print 'Decrypted string:', decoded, type(decoded), decoded.decode('utf8')
    print '--------------mobile'
    encoded = encrypt(u'12145677654'.encode('utf8'))
    print 'Encrypted string:', encoded, len(encoded)
    decoded = decrypt(encoded)
    print 'Decrypted string:', decoded, type(decoded), decoded.decode('utf8')
    print '--------------bank_card'
    encoded = encrypt(u'abcde67890123456789012345'.encode('utf8'))
    print 'Encrypted string:', encoded, len(encoded)
    decoded = decrypt(encoded)
    print 'Decrypted string:', decoded, type(decoded), decoded.decode('utf8')