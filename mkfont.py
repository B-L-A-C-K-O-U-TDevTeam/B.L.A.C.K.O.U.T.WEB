#!/usr/bin/env python3
"""
BLACKOUT CIPHER — a display typeface drawn from scratch for the B.L.A.C.K.O.U.T. site.

Design system
-------------
Everything sits on a rigid orthogonal lattice: uprights, crossbars, and 45-degree
chamfers only. Outer silhouette corners are cut (machined bevel, C); free stem ends
get a much smaller cut (Cs) so they read as sheared metal rather than points.
Numerals are built on a seven-segment skeleton (period-correct for a 1970s console)
and zero carries a cipher slash. Uppercase only; lowercase codepoints are mapped
onto the same glyphs so the face never falls back mid-word.
"""
import math, os, sys
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

UPM = 1000
H   = 700          # cap height
S   = int(os.environ.get("BLKT_STROKE", 118))   # stroke weight
C   = 96           # outer silhouette bevel
Cs  = 30           # free stem-end bevel
W   = 470          # standard body width
SB  = 56           # side bearing

MIDY = 291         # bottom of the middle crossbar
MIDT = MIDY + S    # top of the middle crossbar


# ---------------------------------------------------------------- primitives
def rect(x0, y0, x1, y1, tl=0, tr=0, br=0, bl=0):
    """Axis-aligned rectangle with optional 45-degree corner cuts."""
    pts = [
        (x0 + bl, y0), (x1 - br, y0),
        (x1, y0 + br), (x1, y1 - tr),
        (x1 - tr, y1), (x0 + tl, y1),
        (x0, y1 - tl), (x0, y0 + bl),
    ]
    out = []
    for p in pts:
        if not out or (abs(p[0] - out[-1][0]) > .5 or abs(p[1] - out[-1][1]) > .5):
            out.append(p)
    if len(out) > 2 and abs(out[0][0] - out[-1][0]) < .5 and abs(out[0][1] - out[-1][1]) < .5:
        out.pop()
    return out


def dia(p0, p1, t=S):
    """Diagonal bar between two centreline points, cut square top and bottom."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    th = t * L / max(abs(dy), 1e-6)          # horizontal thickness -> even optical weight
    th = min(th, t * 3.2)
    h = th / 2
    return [(x0 - h, y0), (x0 + h, y0), (x1 + h, y1), (x1 - h, y1)]


def ccw(poly):
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
            for i in range(len(poly)))
    return poly if a > 0 else poly[::-1]


# ------------------------------------------------------- reusable components
def top_bar(w=W, tl=C, tr=C):      return rect(0, H - S, w, H, tl=tl, tr=tr)
def bot_bar(w=W, bl=C, br=C):      return rect(0, 0, w, S, bl=bl, br=br)
def mid_bar(x0=0, x1=W):           return rect(x0, MIDY, x1, MIDT)
def stem_L(y0, y1, **k):           return rect(0, y0, S, y1, **k)
def stem_R(y0, y1, w=W, **k):      return rect(w - S, y0, w, y1, **k)
def free_top(x0, x1, y0):          return rect(x0, y0, x1, H, tl=Cs, tr=Cs)
def free_bot(x0, x1, y1):          return rect(x0, 0, x1, y1, bl=Cs, br=Cs)


G = {}   # char -> (body width, [contours])


def put(ch, body, polys):
    G[ch] = (body, [ccw(p) for p in polys if len(p) > 2])


# ------------------------------------------------------------------ letters
put('A', W, [top_bar(), rect(0, 0, S, H - S, bl=Cs, br=Cs),
              rect(W - S, 0, W, H - S, bl=Cs, br=Cs), rect(0, 240, W, 240 + S)])

put('B', W, [top_bar(tl=0), bot_bar(bl=0), stem_L(0, H), mid_bar(),
              stem_R(MIDT, H - C), stem_R(C, MIDY)])

put('C', W, [top_bar(), bot_bar(), stem_L(C, H - C),
              stem_R(H - C - 105, H - C), stem_R(C, C + 105)])

put('D', W, [top_bar(tl=0), bot_bar(bl=0), stem_L(0, H), stem_R(C, H - C)])

put('E', W, [top_bar(), bot_bar(), stem_L(C, H - C), mid_bar(0, W - 76)])

put('F', W, [top_bar(), rect(0, 0, S, H - C, bl=Cs, br=Cs), mid_bar(0, W - 76)])

put('G', W, [top_bar(), bot_bar(), stem_L(C, H - C), stem_R(H - C - 105, H - C),
              stem_R(C, 366), rect(244, 248, W, 366)])

put('H', W, [free_top(0, S, H - 0) and rect(0, 0, S, H, tl=Cs, tr=Cs, bl=Cs, br=Cs),
              rect(W - S, 0, W, H, tl=Cs, tr=Cs, bl=Cs, br=Cs), mid_bar()])

put('I', S, [rect(0, 0, S, H, tl=Cs, tr=Cs, bl=Cs, br=Cs)])

put('J', 386, [rect(386 - S, C, 386, H, tl=Cs, tr=Cs), bot_bar(386),
                rect(0, C, S, C + 168)])

put('K', W, [rect(0, 0, S, H, tl=Cs, tr=Cs, bl=Cs, br=Cs),
              dia((S + 26, 352), (W - 52, H)), dia((S + 26, 352), (W - 52, 0))])

put('L', W, [rect(0, C, S, H, tl=Cs, tr=Cs), bot_bar()])

put('M', 636, [rect(0, 0, S, H, tl=Cs, tr=Cs, bl=Cs, br=Cs),
                rect(636 - S, 0, 636, H, tl=Cs, tr=Cs, bl=Cs, br=Cs),
                dia((96, H), (318, 236)), dia((318, 236), (540, H))])

put('N', W, [rect(0, 0, S, H, tl=Cs, tr=Cs, bl=Cs, br=Cs),
              rect(W - S, 0, W, H, tl=Cs, tr=Cs, bl=Cs, br=Cs),
              dia((59, H), (W - 59, 0))])

put('O', W, [top_bar(), bot_bar(), stem_L(C, H - C), stem_R(C, H - C)])

put('P', W, [top_bar(), rect(0, 0, S, H - C, bl=Cs, br=Cs), mid_bar(),
              stem_R(MIDT, H - C)])

put('Q', W, [top_bar(), bot_bar(), stem_L(C, H - C), stem_R(C, H - C),
              dia((286, 214), (W - 18, -34))])

put('R', W, [top_bar(), rect(0, 0, S, H - C, bl=Cs, br=Cs), mid_bar(),
              stem_R(MIDT, H - C), dia((214, 352), (W - 52, 0))])

put('S', W, [top_bar(), bot_bar(), mid_bar(),
              stem_L(MIDT, H - C), stem_R(C, MIDY)])

put('T', W, [top_bar(), rect((W - S) / 2, 0, (W + S) / 2, H - S, bl=Cs, br=Cs)])

put('U', W, [rect(0, C, S, H, tl=Cs, tr=Cs), rect(W - S, C, W, H, tl=Cs, tr=Cs), bot_bar()])

put('V', W, [dia((60, H), (W / 2, 0)), dia((W - 60, H), (W / 2, 0)),
              rect(W / 2 - S / 2, 0, W / 2 + S / 2, 96, bl=Cs, br=Cs)])

put('W', 636, [dia((62, H), (196, 0)), dia((196, 0), (318, 430)),
                dia((318, 430), (440, 0)), dia((440, 0), (574, H))])

put('X', W, [dia((60, H), (W - 60, 0)), dia((W - 60, H), (60, 0))])

put('Y', W, [dia((60, H), (W / 2, 330)), dia((W - 60, H), (W / 2, 330)),
              rect((W - S) / 2, 0, (W + S) / 2, 388, bl=Cs, br=Cs)])

put('Z', W, [top_bar(), bot_bar(), dia((W - 62, H - S + 10), (62, S - 10))])

# ----------------------------------------------------------------- numerals
UL = lambda: stem_L(MIDT, H - C)
LL = lambda: stem_L(C, MIDY)
UR = lambda: stem_R(MIDT, H - C)
LR = lambda: stem_R(C, MIDY)

put('0', W, [top_bar(), bot_bar(), stem_L(C, H - C), stem_R(C, H - C),
              dia((126, 150), (W - 126, H - 150))])                     # cipher slash
put('1', W, [rect((W - S) / 2, 0, (W + S) / 2, H, tl=Cs, tr=Cs),
              dia(((W - S) / 2 + 16, H - 34), ((W - S) / 2 - 150, H - 200), t=112),
              rect(74, 0, W - 74, S, bl=Cs, br=Cs)])
put('2', W, [top_bar(), UR(), mid_bar(), LL(), bot_bar()])
put('3', W, [top_bar(), UR(), mid_bar(), LR(), bot_bar()])
put('4', W, [UL(), UR(), mid_bar(), rect(W - S, 0, W, MIDY, bl=Cs, br=Cs)])
put('5', W, [top_bar(), UL(), mid_bar(), LR(), bot_bar()])
put('6', W, [top_bar(), UL(), mid_bar(), LL(), LR(), bot_bar()])
put('7', W, [top_bar(), rect(W - S, 0, W, H - C, bl=Cs, br=Cs)])
put('8', W, [top_bar(), UL(), UR(), mid_bar(), LL(), LR(), bot_bar()])
put('9', W, [top_bar(), UL(), UR(), mid_bar(), LR(), bot_bar()])

# ------------------------------------------------------------- punctuation
put('.',  S,   [rect(0, 0, S, S)])
put(',',  S,   [rect(0, 0, S, S), dia((S / 2, 30), (S / 2 - 62, -132), t=96)])
put(':',  S,   [rect(0, 118, S, 118 + S), rect(0, 430, S, 430 + S)])
put(';',  S,   [rect(0, 430, S, 430 + S), rect(0, 0, S, S),
                 dia((S / 2, 30), (S / 2 - 62, -132), t=96)])
put('!',  S,   [rect(0, 216, S, H, tl=Cs, tr=Cs), rect(0, 0, S, S)])
put('?',  W,   [top_bar(), stem_R(MIDT, H - C), mid_bar((W - S) / 2, W),
                 rect((W - S) / 2, 168, (W + S) / 2, MIDY), rect((W - S) / 2, 0, (W + S) / 2, S)])
put('/',  W,   [dia((16, -60), (W - 16, H + 60))])
put('\\', W,   [dia((16, H + 60), (W - 16, -60))])
put('-',  300, [rect(0, MIDY, 300, MIDT)])
put('\u2013', 400, [rect(0, MIDY, 400, MIDT)])
put('\u2014', 600, [rect(0, MIDY, 600, MIDT)])
put('_',  W,   [rect(0, -130, W, -130 + S)])
put('\u00b7', S, [rect(0, MIDY, S, MIDT)])
put("'",  S,   [rect(0, H - 214, S, H, tl=Cs, tr=Cs)])
put('"',  296, [rect(0, H - 214, S, H, tl=Cs, tr=Cs), rect(178, H - 214, 296, H, tl=Cs, tr=Cs)])
put('(',  196, [rect(0, C, S, H - C), rect(0, H - S, 196, H, tl=Cs, tr=Cs),
                 rect(0, 0, 196, S, bl=Cs, br=Cs)])
put(')',  196, [rect(196 - S, C, 196, H - C), rect(0, H - S, 196, H, tl=Cs, tr=Cs),
                 rect(0, 0, 196, S, bl=Cs, br=Cs)])
put('[',  196, [rect(0, 0, S, H), rect(0, H - S, 196, H), rect(0, 0, 196, S)])
put(']',  196, [rect(196 - S, 0, 196, H), rect(0, H - S, 196, H), rect(0, 0, 196, S)])
put('+',  W,   [rect(52, MIDY, W - 52, MIDT), rect((W - S) / 2, 175, (W + S) / 2, 525)])
put('=',  W,   [rect(52, 186, W - 52, 304), rect(52, 396, W - 52, 514)])
put('*',  W,   [rect((W - S) / 2, 380, (W + S) / 2, H),
                 dia((70, H - 60), (W - 70, 440), t=96), dia((W - 70, H - 60), (70, 440), t=96)])
put('#',  W,   [rect(96, 168, 214, 588), rect(W - 214, 168, W - 96, 588),
                 rect(0, 260, W, 348), rect(0, 430, W, 518)])
put('%',  W,   [rect(0, H - 200, 176, H), rect(W - 176, 0, W, 200), dia((30, 0), (W - 30, H), t=96)])
put('$',  W,   [top_bar(), bot_bar(), mid_bar(), stem_L(MIDT, H - C), stem_R(C, MIDY),
                 rect((W - 84) / 2, -80, (W + 84) / 2, H + 80)])
put('&',  W,   [top_bar(tl=Cs, tr=Cs), stem_L(MIDT, H - C), stem_R(MIDT, H - C),
                 mid_bar(), stem_L(C, MIDY), bot_bar(), dia((250, 250), (W + 30, -70))])
put('<',  W,   [dia((W - 70, H - 90), (90, 350), t=104), dia((90, 350), (W - 70, 90), t=104)])
put('>',  W,   [dia((70, H - 90), (W - 90, 350), t=104), dia((W - 90, 350), (70, 90), t=104)])
put('\u00d7', W, [dia((110, H - 140), (W - 110, 140), t=100), dia((W - 110, H - 140), (110, 140), t=100)])
put('\u00b0', 260, [rect(0, H - 260, 260, H - 142), rect(0, H - 260, 118, H),
                     rect(142, H - 260, 260, H), rect(0, H - 118, 260, H)])
put('@',  W,   [top_bar(), bot_bar(), stem_L(C, H - C), stem_R(H - C - 150, H - C),
                 rect(160, 190, 350, 308), rect(232, 190, 350, 450), rect(160, 396, 350, 450)])

NAME  = "Blackout Cipher"
STYLE = os.environ.get("BLKT_STYLE", "Regular")
WGHT  = int(os.environ.get("BLKT_WEIGHT", 400))
OUT   = os.environ.get("BLKT_OUT", "blackout-cipher")


def build():
    order = ['.notdef', 'space'] + [f'g{ord(c):04X}' for c in G]
    pen_glyphs, advances, cmap = {}, {}, {}

    pen = TTGlyphPen(None); pen_glyphs['.notdef'] = pen.glyph(); advances['.notdef'] = 400
    pen = TTGlyphPen(None); pen_glyphs['space'] = pen.glyph(); advances['space'] = 300
    cmap[0x20] = 'space'
    cmap[0xA0] = 'space'

    for ch, (body, polys) in G.items():
        name = f'g{ord(ch):04X}'
        sb = 91 if ch in '.,:;!\'' or body <= S else SB
        p = TTGlyphPen(None)
        for poly in polys:
            p.moveTo((round(poly[0][0] + sb), round(poly[0][1])))
            for pt in poly[1:]:
                p.lineTo((round(pt[0] + sb), round(pt[1])))
            p.closePath()
        pen_glyphs[name] = p.glyph()
        advances[name] = round(body + 2 * sb)
        cmap[ord(ch)] = name
        if ch.isalpha():
            cmap[ord(ch.lower())] = name          # lowercase never falls back

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(pen_glyphs)
    fb.setupHorizontalMetrics({g: (advances[g], 0) for g in order})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({
        "familyName": NAME, "styleName": STYLE,
        "psName": "BlackoutCipher-" + STYLE,
        "version": "1.0", "copyright": "Drawn for the B.L.A.C.K.O.U.T. project.",
    })
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200,
                sCapHeight=H, achVendID="BLKT", usWeightClass=WGHT,
                fsSelection=(1 << 5) if WGHT >= 700 else (1 << 6))
    fb.setupPost(isFixedPitch=0)
    fb.font["head"].macStyle = 1 if WGHT >= 700 else 0
    fb.font.flavor = "woff"                       # WOFF 1 = zlib, no brotli needed
    fb.save(OUT + ".woff")
    fb.font.flavor = None
    fb.save(OUT + ".ttf")
    print("glyphs:", len(G), "+ space")


if __name__ == "__main__":
    build()
