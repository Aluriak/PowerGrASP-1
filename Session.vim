let SessionLoad = 1
if &cp | set nocp | endif
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
exe "cd " . escape(expand("<sfile>:p:h"), ' ')
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +1 asprgc/__main__.py
badd +1 asprgc/aspsolver.py
badd +1 data/extract.lp
badd +1 data/findconcept.lp
badd +8 data.py
badd +2 asprgc/data.py
badd +15 asprgc/asperge.py
badd +3 asprgc/logger.py
badd +1 asprgc/commons.py
badd +1 setup.py
badd +1 asprgc/asprgc.py
badd +1 data/firstmodel.lp
badd +1 data/findcliques.lp
badd +1 ~/ASP/test/powercomp4.lp
badd +23 data/diamond.lp
badd +1 data/update.lp
badd +1 data/model.lp
badd +1 asprgc/atoms.py
badd +1 data/findbestconcept.lp
badd +1 data/edgeupdate.lp
badd +1 debug/findbestconcept.lp
badd +1 debug/threenode.lp
badd +1 remains.lp
badd +1 data/remains.lp
badd +1 asprgc/ASPsources/extract.lp
badd +1 asprgc/ASPsources/findbestconcept.lp
badd +1 asprgc/ASPsources/edgeupdate.lp
badd +1 asprgc/ASPsources/remains.lp
badd +1 asprgc/converter/converter.py
badd +22 asprgc/ASPsources/inclusion.lp
badd +30 debug/inclusion.lp
badd +1 asprgc/converter/bbl.py
argglobal
silent! argdel *
set stal=2
edit setup.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 27 - ((26 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
27
normal! 0
lcd ~/ASP/test/rewritting/asprgc
tabedit ~/ASP/test/rewritting/asprgc/asprgc/__main__.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 16 - ((15 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
16
normal! 078|
lcd ~/ASP/test/rewritting/asprgc
tabedit ~/ASP/test/rewritting/asprgc/asprgc/asprgc.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 151 - ((49 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
151
normal! 01|
lcd ~/ASP/test/rewritting/asprgc
tabedit ~/ASP/test/rewritting/asprgc/asprgc/commons.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 37 - ((36 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
37
normal! 011|
lcd ~/ASP/test/rewritting/asprgc
tabedit ~/ASP/test/rewritting/asprgc/asprgc/atoms.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 1 - ((0 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
1
normal! 03|
lcd ~/ASP/test/rewritting/asprgc
tabedit ~/ASP/test/rewritting/asprgc/asprgc/converter/converter.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
silent! normal! zE
let s:l = 69 - ((10 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
69
normal! 018|
lcd ~/ASP/test/rewritting/asprgc
tabedit ~/ASP/test/rewritting/asprgc/asprgc/converter/bbl.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
silent! normal! zE
let s:l = 158 - ((19 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
158
normal! 01|
lcd ~/ASP/test/rewritting/asprgc
tabedit ~/ASP/test/rewritting/asprgc/asprgc/ASPsources/extract.lp
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
silent! normal! zE
let s:l = 47 - ((37 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
47
normal! 0
lcd ~/ASP/test/rewritting/asprgc
tabedit ~/ASP/test/rewritting/asprgc/asprgc/ASPsources/findbestconcept.lp
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
silent! normal! zE
let s:l = 49 - ((17 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
49
normal! 052|
lcd ~/ASP/test/rewritting/asprgc
tabedit ~/ASP/test/rewritting/asprgc/asprgc/ASPsources/remains.lp
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
silent! normal! zE
let s:l = 9 - ((8 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
9
normal! 0
lcd ~/ASP/test/rewritting/asprgc
tabedit ~/ASP/test/rewritting/asprgc/asprgc/ASPsources/inclusion.lp
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
silent! normal! zE
let s:l = 55 - ((48 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
55
normal! 013|
lcd ~/ASP/test/rewritting/asprgc
tabedit ~/ASP/test/rewritting/asprgc/debug/inclusion.lp
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
silent! normal! zE
let s:l = 47 - ((39 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
47
normal! 0
lcd ~/ASP/test/rewritting/asprgc
tabnext 9
set stal=1
if exists('s:wipebuf')
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxtToO
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
