# -*- mode: python -*-
a = Analysis(['gradeDay.py'],
             pathex=['C:\\Users\\Joseph\\Documents\\projects\\python\\gradeDay'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='gradeDay.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='alert.ico')
coll = COLLECT(exe,
               a.binaries,
               [('alert-icon.png','alert-icon.png','DATA')],
               [('close.png','close.png','DATA')],
               [('info.png','info.png','DATA')],
               [('LICENSE','LICENSE','DATA')],
               [('voicealert.wav','voicealert.wav','DATA')],
               [('about.html','about.html','DATA')],
               Tree('images', prefix = 'images'),
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='gradeDay')
