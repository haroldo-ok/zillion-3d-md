"""Compiled wall scalers: for every on-screen wall height a tiny 68000 routine
   that copies the right texel for each screen row into the column buffer.
   a0 = texture column (64 bytes), a1 = first destination row.
   Uses 4-byte 12-cycle indirect/post-increment moves ((a0) / (a0)+) whenever
   consecutive screen rows sample the same or next sequential texel (all walls
   with H >= 64, plus repeated runs), falling back to 16-cycle d16(a0) when a
   row skips ahead by >= 2 texels."""
from cgen import *
import config as C

MOVEB_D16 = 0x1368   # move.b d16(a0),d16(a1)  (16 cyc, 6 B)
MOVEB_IND = 0x1350   # move.b (a0),d16(a1)     (12 cyc, 4 B)
MOVEB_INC = 0x1358   # move.b (a0)+,d16(a1)    (12 cyc, 4 B)
LEA_A0    = 0x41E8   # lea d16(a0),a0          ( 8 cyc, 4 B)
RTS       = 0x4E75

def variant(H):
    """code words for wall height H (rows drawn = min(H, VIEWH))"""
    step = min(0xFFFFFF, (64 << 16) // H)
    if H >= C.VIEWH:
        n = C.VIEWH
        pos = ((H - C.VIEWH) >> 1) * step + (step >> 1)
    else:
        n = H
        pos = step >> 1
    ts = []
    for _ in range(n):
        ts.append(min(63, pos >> 16))
        pos += step

    w = []
    cur = 0
    if n >= 2 and ts[0] > 0 and (ts[1] == ts[0] or ts[1] == ts[0] + 1):
        w += [LEA_A0, ts[0]]
        cur = ts[0]
    for r, t in enumerate(ts):
        nxt = ts[r + 1] if r + 1 < n else -1
        if t == cur:
            if nxt == cur + 1:
                w += [MOVEB_INC, 4 * r]
                cur += 1
            else:
                w += [MOVEB_IND, 4 * r]
        else:
            w += [MOVEB_D16, (t - cur) & 0xFFFF, 4 * r]
    w.append(RTS)
    return w

def heights():
    # index i: i<=VIEWH -> H=i ; i>VIEWH -> H = VIEWH + 2*(i-VIEWH)
    hs = [0] + list(range(1, C.VIEWH + 1))
    h = C.VIEWH + 2
    while h <= 512:
        hs.append(h)
        h += 2
    return hs

def gen_scalers(outdir):
    code = []
    ofs = []
    for H in heights():
        ofs.append(len(code) * 2)
        code += variant(max(H, 1))
    t = '#include "gen.h"\n'
    t += c_words("scaler_ofs", ofs, "u32")
    t += c_words("scaler_code", code, "u16", per_line=16, align=2)
    write(os.path.join(outdir, "src/gen/scalers.c"), t)
    return len(code) * 2, len(ofs)
