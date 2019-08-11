from trees import *
from vl_codes import *
import arithmetic 
import arithmeticac
import condarithmetic
import adconarithmetic2
import adconarithmetic
from itertools import groupby
from json import dump
from sys import argv


def camzip(method, filename, b=0.1, num=0, scale=(100000,1),pr=0,pc=0 ):

    with open(filename, 'rb') as fin: #*
        x = fin.read()

    frequencies = dict([(key, len(list(group))) for key, group in groupby(sorted(x))])
    n = sum([frequencies[a] for a in frequencies])
    p = dict([(a,frequencies[a]/n) for a in frequencies])

    if method == 'huffman' or method == 'shannon_fano':
        if (method == 'huffman'):
            xt = huffman(p)
            c = xtree2code(xt)
        else:
            c = shannon_fano(p)
            xt = code2xtree(c)

        y = vl_encode(x, c)

    elif method == 'arithmetic':
        y = arithmetic.encode(x,p)
    elif method == 'carithmeticac':
        y = arithmeticac.encode(x,b,num,scale)
    elif method == 'iadhuffman':
        y = adhuffman(x,pr)
    elif method == 'fcondarithmetic':
        y = condarithmetic.encode(x,pc)
    elif method == 'gadconarithmetic':
        y = adconarithmetic.encode(x,b)
    elif method == 'jadconarithmetic':
        y = adconarithmetic2.encode(x,b)

    else:
        raise NameError('Compression method %s unknown' % method)
    
    
    y = bytes(bits2bytes(y))
    
    outfile = filename + '.cz' + method[0]

    with open(outfile, 'wb') as fout:
        fout.write(y)

    pfile = filename + '.czp'
    n = len(x)

    with open(pfile, 'w') as fp:
        dump(frequencies, fp)


if __name__ == "__main__":
    if (len(argv) != 3):
        print('Usage: python %s compression_method filename\n' % argv[0])
        print('Example: python %s huffman hamlet.txt' % argv[0])
        print('or:      python %s shannon_fano hamlet.txt' % argv[0])
        print('or:      python %s arithmetic hamlet.txt' % argv[0])
        exit()

    camzip(argv[1], argv[2])

