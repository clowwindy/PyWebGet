# -*- encoding: utf-8 -*-
#
# __author__ = 'clowwindy'

from thr import argparse
from thr import shlex
# Note that a modified version of shlex is used to be able to handle unicode

def parse_args(param_string):
    """
    return: url, cookie, referer, filename
    >>> print parse_args(u'wget -o CrystalDiskInfo4\u4f60\u597d_1_3-en.exe --header="Cookie: gdriveid=015576B414E964A2C77DF87A1470A556" --referer="http://lixian.vip.xulei.com/" "http://gdl.lixian.vip.xunlei.com/download?fid=D7iJ8CYbsYnZJp3YyMpg7Auk0zWQIBoAAAAAAKR3v9ij9w2CpMgGIOZ3IDwSEK5N&mid=666&threshold=150&tid=89F300566E1799F7E1D2AC643A4385DE&srcid=4&verno=1&g=A477BFD8A3F70D82A4C80620E677203C1210AE4D&scn=c8&i=A477BFD8A3F70D82A4C80620E677203C1210AE4D&t=0&ui=28118228&ti=41286564353&s=1712272&m=0&n=0122439D2C74616C4408428F166E666F343E00BB6C2D656E2E0449815F00000000"')
    (u'http://gdl.lixian.vip.xunlei.com/download?fid=D7iJ8CYbsYnZJp3YyMpg7Auk0zWQIBoAAAAAAKR3v9ij9w2CpMgGIOZ3IDwSEK5N&mid=666&threshold=150&tid=89F300566E1799F7E1D2AC643A4385DE&srcid=4&verno=1&g=A477BFD8A3F70D82A4C80620E677203C1210AE4D&scn=c8&i=A477BFD8A3F70D82A4C80620E677203C1210AE4D&t=0&ui=28118228&ti=41286564353&s=1712272&m=0&n=0122439D2C74616C4408428F166E666F343E00BB6C2D656E2E0449815F00000000', u'gdriveid=015576B414E964A2C77DF87A1470A556', u'http://lixian.vip.xulei.com/', u'CrystalDiskInfo4\u4f60\u597d_1_3-en.exe')

    """

    params = shlex.split(param_string)
    if len(params) > 1:
        if params[0] == 'wget':
            params = params[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument('-o','--output-file')
    parser.add_argument('--header')
    parser.add_argument('--referer')
    parser.add_argument('-t')
    parser.add_argument('url', metavar='N', nargs=1)
    args = parser.parse_known_args(params)[0]

    cookie = args.header
    if cookie and cookie.find("Cookie: ")==0:
        cookie = cookie[8:]

    referer = args.referer
    url = args.url
    if len(url) > 0:
        url = url[0]
    else:
        return None

    return url, cookie, referer, args.output_file