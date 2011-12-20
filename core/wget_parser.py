# -*- encoding: utf-8 -*-
#
# __author__ = 'clowwindy'

from thr import argparse
from thr import shlex
# Note that a modified version of shlex is used to be able to handle unicode

def parse_args(param_string):
    """
    return: url, cookie, referer, filename
    """

    params = shlex.split(param_string)
    if len(params) > 1:
        if params[0] == 'wget':
            params = params[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument('-O','--output-document')
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

    return url, cookie, referer, args.output_document