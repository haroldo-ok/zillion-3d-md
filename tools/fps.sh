#!/bin/sh
# usage: fps.sh [ROM] -> renders in 1190 vblanks standing still in the start view (after turning left)
ROM=${1:-out/rom.bin}
mkdir -p /tmp/shots
rm -f /tmp/shots/f*
./tools/harness /root/work/gpgx/genesis_plus_gx_libretro.so $ROM 4100 "1000-1003:start,1300-1303:c,1700-1703:c,2000-2003:c,2600-2700:left,shot@2700,shot@3890" /tmp/shots/f >/dev/null 2>&1
python3 - <<'P'
import subprocess
def v(f):
    o=subprocess.run(['python3','tools/ramsym.py',f,'dbg_frames:4'],capture_output=True,text=True).stdout.split()
    x=int(o[2],16); return ((x&0xff00)>>8)|(((x>>24)&0xff)<<8)
a=v('/tmp/shots/f2700.ram'); b=v('/tmp/shots/f3890.ram')
print("renders in 1190 vblanks:", (b-a)&0xffff, " => %.2f fps"%(((b-a)&0xffff)/19.8))
P
