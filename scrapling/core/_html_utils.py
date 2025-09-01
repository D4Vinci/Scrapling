"""
This file is mostly copied from the submodule `w3lib.html` source code to stop downloading the whole library to use a small part of it.
So the goal of doing this is to minimize the memory footprint and keep the library size relatively smaller.
Repo source code: https://github.com/scrapy/w3lib/blob/master/w3lib/html.py
"""

from re import compile as _re_compile, IGNORECASE

from scrapling.core._types import Iterable, Optional, Match, StrOrBytes

_ent_re = _re_compile(
    r"&((?P<named>[a-z\d]+)|#(?P<dec>\d+)|#x(?P<hex>[a-f\d]+))(?P<semicolon>;?)",
    IGNORECASE,
)
# maps HTML4 entity name to the Unicode code point
name2codepoint = {
    "AElig": 0x00C6,  # latin capital letter AE = latin capital ligature AE, U+00C6 ISOlat1
    "Aacute": 0x00C1,  # latin capital letter A with acute, U+00C1 ISOlat1
    "Acirc": 0x00C2,  # latin capital letter A with circumflex, U+00C2 ISOlat1
    "Agrave": 0x00C0,  # latin capital letter A with grave = latin capital letter A grave, U+00C0 ISOlat1
    "Alpha": 0x0391,  # greek capital letter alpha, U+0391
    "Aring": 0x00C5,  # latin capital letter A with the ring above = latin capital letter A ring, U+00C5 ISOlat1
    "Atilde": 0x00C3,  # latin capital letter A with tilde, U+00C3 ISOlat1
    "Auml": 0x00C4,  # latin capital letter A with diaeresis, U+00C4 ISOlat1
    "Beta": 0x0392,  # greek capital letter beta, U+0392
    "Ccedil": 0x00C7,  # latin capital letter C with cedilla, U+00C7 ISOlat1
    "Chi": 0x03A7,  # greek capital letter chi, U+03A7
    "Dagger": 0x2021,  # double dagger, U+2021 ISOpub
    "Delta": 0x0394,  # greek capital letter delta, U+0394 ISOgrk3
    "ETH": 0x00D0,  # latin capital letter ETH, U+00D0 ISOlat1
    "Eacute": 0x00C9,  # latin capital letter E with acute, U+00C9 ISOlat1
    "Ecirc": 0x00CA,  # latin capital letter E with circumflex, U+00CA ISOlat1
    "Egrave": 0x00C8,  # latin capital letter E with grave, U+00C8 ISOlat1
    "Epsilon": 0x0395,  # greek capital letter epsilon, U+0395
    "Eta": 0x0397,  # greek capital letter eta, U+0397
    "Euml": 0x00CB,  # latin capital letter E with diaeresis, U+00CB ISOlat1
    "Gamma": 0x0393,  # greek capital letter gamma, U+0393 ISOgrk3
    "Iacute": 0x00CD,  # latin capital letter I with acute, U+00CD ISOlat1
    "Icirc": 0x00CE,  # latin capital letter I with circumflex, U+00CE ISOlat1
    "Igrave": 0x00CC,  # latin capital letter I with grave, U+00CC ISOlat1
    "Iota": 0x0399,  # greek capital letter iota, U+0399
    "Iuml": 0x00CF,  # latin capital letter I with diaeresis, U+00CF ISOlat1
    "Kappa": 0x039A,  # greek capital letter kappa, U+039A
    "Lambda": 0x039B,  # greek capital letter lambda, U+039B ISOgrk3
    "Mu": 0x039C,  # greek capital letter mu, U+039C
    "Ntilde": 0x00D1,  # latin capital letter N with tilde, U+00D1 ISOlat1
    "Nu": 0x039D,  # greek capital letter nu, U+039D
    "OElig": 0x0152,  # latin capital ligature OE, U+0152 ISOlat2
    "Oacute": 0x00D3,  # latin capital letter O with acute, U+00D3 ISOlat1
    "Ocirc": 0x00D4,  # latin capital letter O with circumflex, U+00D4 ISOlat1
    "Ograve": 0x00D2,  # latin capital letter O with grave, U+00D2 ISOlat1
    "Omega": 0x03A9,  # greek capital letter omega, U+03A9 ISOgrk3
    "Omicron": 0x039F,  # greek capital letter omicron, U+039F
    "Oslash": 0x00D8,  # latin capital letter O with stroke = latin capital letter O slash, U+00D8 ISOlat1
    "Otilde": 0x00D5,  # latin capital letter O with tilde, U+00D5 ISOlat1
    "Ouml": 0x00D6,  # latin capital letter O with diaeresis, U+00D6 ISOlat1
    "Phi": 0x03A6,  # greek capital letter phi, U+03A6 ISOgrk3
    "Pi": 0x03A0,  # greek capital letter pi, U+03A0 ISOgrk3
    "Prime": 0x2033,  # double prime = seconds = inches, U+2033 ISOtech
    "Psi": 0x03A8,  # greek capital letter psi, U+03A8 ISOgrk3
    "Rho": 0x03A1,  # greek capital letter rho, U+03A1
    "Scaron": 0x0160,  # latin capital letter S with caron, U+0160 ISOlat2
    "Sigma": 0x03A3,  # greek capital letter sigma, U+03A3 ISOgrk3
    "THORN": 0x00DE,  # latin capital letter THORN, U+00DE ISOlat1
    "Tau": 0x03A4,  # greek capital letter tau, U+03A4
    "Theta": 0x0398,  # greek capital letter theta, U+0398 ISOgrk3
    "Uacute": 0x00DA,  # latin capital letter U with acute, U+00DA ISOlat1
    "Ucirc": 0x00DB,  # latin capital letter U with circumflex, U+00DB ISOlat1
    "Ugrave": 0x00D9,  # latin capital letter U with grave, U+00D9 ISOlat1
    "Upsilon": 0x03A5,  # greek capital letter upsilon, U+03A5 ISOgrk3
    "Uuml": 0x00DC,  # latin capital letter U with diaeresis, U+00DC ISOlat1
    "Xi": 0x039E,  # greek capital letter xi, U+039E ISOgrk3
    "Yacute": 0x00DD,  # latin capital letter Y with acute, U+00DD ISOlat1
    "Yuml": 0x0178,  # latin capital letter Y with diaeresis, U+0178 ISOlat2
    "Zeta": 0x0396,  # greek capital letter zeta, U+0396
    "aacute": 0x00E1,  # latin small letter a with acute, U+00E1 ISOlat1
    "acirc": 0x00E2,  # latin small letter a with circumflex, U+00E2 ISOlat1
    "acute": 0x00B4,  # acute accent = spacing acute, U+00B4 ISOdia
    "aelig": 0x00E6,  # latin small letter ae = latin small ligature ae, U+00E6 ISOlat1
    "agrave": 0x00E0,  # latin small letter a with grave = latin small letter a grave, U+00E0 ISOlat1
    "alefsym": 0x2135,  # alef symbol = first transfinite cardinal, U+2135 NEW
    "alpha": 0x03B1,  # greek small letter alpha, U+03B1 ISOgrk3
    "amp": 0x0026,  # ampersand, U+0026 ISOnum
    "and": 0x2227,  # logical and = wedge, U+2227 ISOtech
    "ang": 0x2220,  # angle, U+2220 ISOamso
    "aring": 0x00E5,  # latin small letter a with the ring above = latin small letter a ring, U+00E5 ISOlat1
    "asymp": 0x2248,  # almost equal to = asymptotic to, U+2248 ISOamsr
    "atilde": 0x00E3,  # latin small letter a with tilde, U+00E3 ISOlat1
    "auml": 0x00E4,  # latin small letter a with diaeresis, U+00E4 ISOlat1
    "bdquo": 0x201E,  # double low-9 quotation mark, U+201E NEW
    "beta": 0x03B2,  # greek small letter beta, U+03B2 ISOgrk3
    "brvbar": 0x00A6,  # broken bar = broken vertical bar, U+00A6 ISOnum
    "bull": 0x2022,  # bullet = black small circle, U+2022 ISOpub
    "cap": 0x2229,  # intersection = cap, U+2229 ISOtech
    "ccedil": 0x00E7,  # latin small letter c with cedilla, U+00E7 ISOlat1
    "cedil": 0x00B8,  # cedilla = spacing cedilla, U+00B8 ISOdia
    "cent": 0x00A2,  # cent sign, U+00A2 ISOnum
    "chi": 0x03C7,  # greek small letter chi, U+03C7 ISOgrk3
    "circ": 0x02C6,  # modifier letter circumflex accent, U+02C6 ISOpub
    "clubs": 0x2663,  # black club suit = shamrock, U+2663 ISOpub
    "cong": 0x2245,  # approximately equal to, U+2245 ISOtech
    "copy": 0x00A9,  # copyright sign, U+00A9 ISOnum
    "crarr": 0x21B5,  # downwards arrow with corner leftwards = carriage return, U+21B5 NEW
    "cup": 0x222A,  # union = cup, U+222A ISOtech
    "curren": 0x00A4,  # currency sign, U+00A4 ISOnum
    "dArr": 0x21D3,  # downwards double arrow, U+21D3 ISOamsa
    "dagger": 0x2020,  # dagger, U+2020 ISOpub
    "darr": 0x2193,  # downwards arrow, U+2193 ISOnum
    "deg": 0x00B0,  # degree sign, U+00B0 ISOnum
    "delta": 0x03B4,  # greek small letter delta, U+03B4 ISOgrk3
    "diams": 0x2666,  # black diamond suit, U+2666 ISOpub
    "divide": 0x00F7,  # division sign, U+00F7 ISOnum
    "eacute": 0x00E9,  # latin small letter e with acute, U+00E9 ISOlat1
    "ecirc": 0x00EA,  # latin small letter e with circumflex, U+00EA ISOlat1
    "egrave": 0x00E8,  # latin small letter e with grave, U+00E8 ISOlat1
    "empty": 0x2205,  # empty set = null set = diameter, U+2205 ISOamso
    "emsp": 0x2003,  # em space, U+2003 ISOpub
    "ensp": 0x2002,  # en space, U+2002 ISOpub
    "epsilon": 0x03B5,  # greek small letter epsilon, U+03B5 ISOgrk3
    "equiv": 0x2261,  # identical to, U+2261 ISOtech
    "eta": 0x03B7,  # greek small letter eta, U+03B7 ISOgrk3
    "eth": 0x00F0,  # latin small letter eth, U+00F0 ISOlat1
    "euml": 0x00EB,  # latin small letter e with diaeresis, U+00EB ISOlat1
    "euro": 0x20AC,  # euro sign, U+20AC NEW
    "exist": 0x2203,  # there exists, U+2203 ISOtech
    "fnof": 0x0192,  # latin small f with hook = function = florin, U+0192 ISOtech
    "forall": 0x2200,  # for all, U+2200 ISOtech
    "frac12": 0x00BD,  # vulgar fraction one half = fraction one half, U+00BD ISOnum
    "frac14": 0x00BC,  # vulgar fraction one quarter = fraction one quarter, U+00BC ISOnum
    "frac34": 0x00BE,  # vulgar fraction three quarters = fraction three quarters, U+00BE ISOnum
    "frasl": 0x2044,  # fraction slash, U+2044 NEW
    "gamma": 0x03B3,  # greek small letter gamma, U+03B3 ISOgrk3
    "ge": 0x2265,  # greater-than or equal to, U+2265 ISOtech
    "gt": 0x003E,  # greater-than sign, U+003E ISOnum
    "hArr": 0x21D4,  # left right double arrow, U+21D4 ISOamsa
    "harr": 0x2194,  # left right arrow, U+2194 ISOamsa
    "hearts": 0x2665,  # black heart suit = valentine, U+2665 ISOpub
    "hellip": 0x2026,  # horizontal ellipsis = three dot leader, U+2026 ISOpub
    "iacute": 0x00ED,  # latin small letter i with acute, U+00ED ISOlat1
    "icirc": 0x00EE,  # latin small letter i with circumflex, U+00EE ISOlat1
    "iexcl": 0x00A1,  # inverted exclamation mark, U+00A1 ISOnum
    "igrave": 0x00EC,  # latin small letter i with grave, U+00EC ISOlat1
    "image": 0x2111,  # blackletter capital I = imaginary part, U+2111 ISOamso
    "infin": 0x221E,  # infinity, U+221E ISOtech
    "int": 0x222B,  # integral, U+222B ISOtech
    "iota": 0x03B9,  # greek small letter iota, U+03B9 ISOgrk3
    "iquest": 0x00BF,  # inverted question mark = turned question mark, U+00BF ISOnum
    "isin": 0x2208,  # element of, U+2208 ISOtech
    "iuml": 0x00EF,  # latin small letter i with diaeresis, U+00EF ISOlat1
    "kappa": 0x03BA,  # greek small letter kappa, U+03BA ISOgrk3
    "lArr": 0x21D0,  # leftwards double arrow, U+21D0 ISOtech
    "lambda": 0x03BB,  # greek small letter lambda, U+03BB ISOgrk3
    "lang": 0x2329,  # left-pointing angle bracket = bra, U+2329 ISOtech
    "laquo": 0x00AB,  # left-pointing double angle quotation mark = left pointing guillemet, U+00AB ISOnum
    "larr": 0x2190,  # leftwards arrow, U+2190 ISOnum
    "lceil": 0x2308,  # left ceiling = apl upstile, U+2308 ISOamsc
    "ldquo": 0x201C,  # left double quotation mark, U+201C ISOnum
    "le": 0x2264,  # less-than or equal to, U+2264 ISOtech
    "lfloor": 0x230A,  # left floor = apl downstile, U+230A ISOamsc
    "lowast": 0x2217,  # asterisk operator, U+2217 ISOtech
    "loz": 0x25CA,  # lozenge, U+25CA ISOpub
    "lrm": 0x200E,  # left-to-right mark, U+200E NEW RFC 2070
    "lsaquo": 0x2039,  # single left-pointing angle quotation mark, U+2039 ISO proposed
    "lsquo": 0x2018,  # left single quotation mark, U+2018 ISOnum
    "lt": 0x003C,  # less-than sign, U+003C ISOnum
    "macr": 0x00AF,  # macron = spacing macron = overline = APL overbar, U+00AF ISOdia
    "mdash": 0x2014,  # em dash, U+2014 ISOpub
    "micro": 0x00B5,  # micro sign, U+00B5 ISOnum
    "middot": 0x00B7,  # middle dot = Georgian comma = Greek middle dot, U+00B7 ISOnum
    "minus": 0x2212,  # minus sign, U+2212 ISOtech
    "mu": 0x03BC,  # greek small letter mu, U+03BC ISOgrk3
    "nabla": 0x2207,  # nabla = backward difference, U+2207 ISOtech
    "nbsp": 0x00A0,  # no-break space = non-breaking space, U+00A0 ISOnum
    "ndash": 0x2013,  # en dash, U+2013 ISOpub
    "ne": 0x2260,  # not equal to, U+2260 ISOtech
    "ni": 0x220B,  # contains as member, U+220B ISOtech
    "not": 0x00AC,  # not sign, U+00AC ISOnum
    "notin": 0x2209,  # not an element of, U+2209 ISOtech
    "nsub": 0x2284,  # not a subset of, U+2284 ISOamsn
    "ntilde": 0x00F1,  # latin small letter n with tilde, U+00F1 ISOlat1
    "nu": 0x03BD,  # greek small letter nu, U+03BD ISOgrk3
    "oacute": 0x00F3,  # latin small letter o with acute, U+00F3 ISOlat1
    "ocirc": 0x00F4,  # latin small letter o with circumflex, U+00F4 ISOlat1
    "oelig": 0x0153,  # latin small ligature oe, U+0153 ISOlat2
    "ograve": 0x00F2,  # latin small letter o with grave, U+00F2 ISOlat1
    "oline": 0x203E,  # overline = spacing overscore, U+203E NEW
    "omega": 0x03C9,  # greek small letter omega, U+03C9 ISOgrk3
    "omicron": 0x03BF,  # greek small letter omicron, U+03BF NEW
    "oplus": 0x2295,  # circled plus = direct sum, U+2295 ISOamsb
    "or": 0x2228,  # logical or = vee, U+2228 ISOtech
    "ordf": 0x00AA,  # feminine ordinal indicator, U+00AA ISOnum
    "ordm": 0x00BA,  # masculine ordinal indicator, U+00BA ISOnum
    "oslash": 0x00F8,  # latin small letter o with stroke, = latin small letter o slash, U+00F8 ISOlat1
    "otilde": 0x00F5,  # latin small letter o with tilde, U+00F5 ISOlat1
    "otimes": 0x2297,  # circled times = vector product, U+2297 ISOamsb
    "ouml": 0x00F6,  # latin small letter o with diaeresis, U+00F6 ISOlat1
    "para": 0x00B6,  # pilcrow sign = paragraph sign, U+00B6 ISOnum
    "part": 0x2202,  # partial differential, U+2202 ISOtech
    "permil": 0x2030,  # per mille sign, U+2030 ISOtech
    "perp": 0x22A5,  # up tack = orthogonal to = perpendicular, U+22A5 ISOtech
    "phi": 0x03C6,  # greek small letter phi, U+03C6 ISOgrk3
    "pi": 0x03C0,  # greek small letter pi, U+03C0 ISOgrk3
    "piv": 0x03D6,  # greek pi symbol, U+03D6 ISOgrk3
    "plusmn": 0x00B1,  # plus-minus sign = plus-or-minus sign, U+00B1 ISOnum
    "pound": 0x00A3,  # pound sign, U+00A3 ISOnum
    "prime": 0x2032,  # prime = minutes = feet, U+2032 ISOtech
    "prod": 0x220F,  # n-ary product = product sign, U+220F ISOamsb
    "prop": 0x221D,  # proportional to, U+221D ISOtech
    "psi": 0x03C8,  # greek small letter psi, U+03C8 ISOgrk3
    "quot": 0x0022,  # quotation mark = APL quote, U+0022 ISOnum
    "rArr": 0x21D2,  # rightwards double arrow, U+21D2 ISOtech
    "radic": 0x221A,  # square root = radical sign, U+221A ISOtech
    "rang": 0x232A,  # right-pointing angle bracket = ket, U+232A ISOtech
    "raquo": 0x00BB,  # right-pointing double angle quotation mark = right pointing guillemet, U+00BB ISOnum
    "rarr": 0x2192,  # rightwards arrow, U+2192 ISOnum
    "rceil": 0x2309,  # right ceiling, U+2309 ISOamsc
    "rdquo": 0x201D,  # right double quotation mark, U+201D ISOnum
    "real": 0x211C,  # blackletter capital R = real part symbol, U+211C ISOamso
    "reg": 0x00AE,  # registered sign = registered trade mark sign, U+00AE ISOnum
    "rfloor": 0x230B,  # right floor, U+230B ISOamsc
    "rho": 0x03C1,  # greek small letter rho, U+03C1 ISOgrk3
    "rlm": 0x200F,  # right-to-left mark, U+200F NEW RFC 2070
    "rsaquo": 0x203A,  # single right-pointing angle quotation mark, U+203A ISO proposed
    "rsquo": 0x2019,  # right single quotation mark, U+2019 ISOnum
    "sbquo": 0x201A,  # single low-9 quotation mark, U+201A NEW
    "scaron": 0x0161,  # latin small letter s with caron, U+0161 ISOlat2
    "sdot": 0x22C5,  # dot operator, U+22C5 ISOamsb
    "sect": 0x00A7,  # section sign, U+00A7 ISOnum
    "shy": 0x00AD,  # soft hyphen = discretionary hyphen, U+00AD ISOnum
    "sigma": 0x03C3,  # greek small letter sigma, U+03C3 ISOgrk3
    "sigmaf": 0x03C2,  # greek small letter final sigma, U+03C2 ISOgrk3
    "sim": 0x223C,  # tilde operator = varies with = similar to, U+223C ISOtech
    "spades": 0x2660,  # black spade suit, U+2660 ISOpub
    "sub": 0x2282,  # subset of, U+2282 ISOtech
    "sube": 0x2286,  # subset of or equal to, U+2286 ISOtech
    "sum": 0x2211,  # n-ary summation, U+2211 ISOamsb
    "sup": 0x2283,  # superset of, U+2283 ISOtech
    "sup1": 0x00B9,  # superscript one = superscript digit one, U+00B9 ISOnum
    "sup2": 0x00B2,  # superscript two = superscript digit two = squared, U+00B2 ISOnum
    "sup3": 0x00B3,  # superscript three = superscript digit three = cubed, U+00B3 ISOnum
    "supe": 0x2287,  # superset of or equal to, U+2287 ISOtech
    "szlig": 0x00DF,  # latin small letter sharp s = ess-zed, U+00DF ISOlat1
    "tau": 0x03C4,  # greek small letter tau, U+03C4 ISOgrk3
    "there4": 0x2234,  # therefore, U+2234 ISOtech
    "theta": 0x03B8,  # greek small letter theta, U+03B8 ISOgrk3
    "thetasym": 0x03D1,  # greek small letter theta symbol, U+03D1 NEW
    "thinsp": 0x2009,  # thin space, U+2009 ISOpub
    "thorn": 0x00FE,  # latin small letter thorn with, U+00FE ISOlat1
    "tilde": 0x02DC,  # small tilde, U+02DC ISOdia
    "times": 0x00D7,  # multiplication sign, U+00D7 ISOnum
    "trade": 0x2122,  # trade mark sign, U+2122 ISOnum
    "uArr": 0x21D1,  # upwards double arrow, U+21D1 ISOamsa
    "uacute": 0x00FA,  # latin small letter u with acute, U+00FA ISOlat1
    "uarr": 0x2191,  # upwards arrow, U+2191 ISOnum
    "ucirc": 0x00FB,  # latin small letter u with circumflex, U+00FB ISOlat1
    "ugrave": 0x00F9,  # latin small letter u with grave, U+00F9 ISOlat1
    "uml": 0x00A8,  # diaeresis = spacing diaeresis, U+00A8 ISOdia
    "upsih": 0x03D2,  # greek upsilon with hook symbol, U+03D2 NEW
    "upsilon": 0x03C5,  # greek small letter upsilon, U+03C5 ISOgrk3
    "uuml": 0x00FC,  # latin small letter u with diaeresis, U+00FC ISOlat1
    "weierp": 0x2118,  # script capital P = power set = Weierstrass p, U+2118 ISOamso
    "xi": 0x03BE,  # greek small letter xi, U+03BE ISOgrk3
    "yacute": 0x00FD,  # latin small letter y with acute, U+00FD ISOlat1
    "yen": 0x00A5,  # yen sign = yuan sign, U+00A5 ISOnum
    "yuml": 0x00FF,  # latin small letter y with diaeresis, U+00FF ISOlat1
    "zeta": 0x03B6,  # greek small letter zeta, U+03B6 ISOgrk3
    "zwj": 0x200D,  # zero width joiner, U+200D NEW RFC 2070
    "zwnj": 0x200C,  # zero width non-joiner, U+200C NEW RFC 2070
}


def to_unicode(
    text: StrOrBytes, encoding: Optional[str] = None, errors: str = "strict"
) -> str:
    """Return the Unicode representation of a bytes object `text`. If `text`
    is already a Unicode object, return it as-is."""
    if isinstance(text, str):
        return text
    if not isinstance(text, (bytes, str)):
        raise TypeError(
            f"to_unicode must receive bytes or str, got {type(text).__name__}"
        )
    if encoding is None:
        encoding = "utf-8"
    return text.decode(encoding, errors)


def _replace_entities(
    text: StrOrBytes,
    keep: Iterable[str] = (),
    remove_illegal: bool = True,
    encoding: str = "utf-8",
) -> str:
    """Remove entities from the given `text` by converting them to their
    corresponding Unicode character.

    `text` can be a Unicode string or a byte string encoded in the given
    `encoding` (which defaults to 'utf-8').

    If `keep` is passed (with a list of entity names), those entities will
    be kept (they won't be removed).

    It supports both numeric entities (``&#nnnn;`` and ``&#hhhh;``)
    and named entities (such as ``&nbsp;`` or ``&gt;``).

    If `remove_illegal` is ``True``, entities that can't be converted are removed.
    If `remove_illegal` is ``False``, entities that can't be converted are kept "as
    is". For more information, see the tests.

    Always returns a Unicode string (with the entities removed).

    >>> _replace_entities(b'Price: &pound;100')
    'Price: \\xa3100'
    >>> print(_replace_entities(b'Price: &pound;100'))
    Price: £100
    >>>

    """

    def convert_entity(m: Match[str]) -> str:
        groups = m.groupdict()
        number = None
        if groups.get("dec"):
            number = int(groups["dec"], 10)
        elif groups.get("hex"):
            number = int(groups["hex"], 16)
        elif groups.get("named"):
            entity_name = groups["named"]
            if entity_name.lower() in keep:
                return m.group(0)
            number = name2codepoint.get(entity_name) or name2codepoint.get(
                entity_name.lower()
            )
        if number is not None:
            # Browsers typically
            # interpret numeric character references in the 80-9F range as representing the characters mapped
            # to bytes 80-9F in the Windows-1252 encoding. For more info
            # see: http://en.wikipedia.org/wiki/Character_encodings_in_HTML
            try:
                if 0x80 <= number <= 0x9F:
                    return bytes((number,)).decode("cp1252")
                return chr(number)
            except (ValueError, OverflowError):  # pragma: no cover
                pass

        return "" if remove_illegal and groups.get("semicolon") else m.group(0)

    return _ent_re.sub(convert_entity, to_unicode(text, encoding))
