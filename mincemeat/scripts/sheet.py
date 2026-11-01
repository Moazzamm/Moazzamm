import sys, glob
from PIL import Image
key=sys.argv[1]; fs=sorted(glob.glob(f'../preview/{key}_*.jpg')); W=6
S=Image.new('RGB',(W*320,((len(fs)+W-1)//W)*180))
for i,f in enumerate(fs):
    im=Image.open(f).resize((320,180)); S.paste(im,((i%W)*320,(i//W)*180))
S.save(f'/tmp/claude-0/-home-user-Moazzamm/813db99a-50da-5c01-8a84-0bedad4272d0/scratchpad/{key}_sheet.jpg')
