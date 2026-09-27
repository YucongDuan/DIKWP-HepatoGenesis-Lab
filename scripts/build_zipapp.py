#!/usr/bin/env python3
"""Build the dependency-free Python executable without bundling private files."""
import argparse
from pathlib import Path
import shutil
import tempfile
import zipapp
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'dist/DIKWP_HepatoGenesis_Lab.pyz');args=p.parse_args()
args.out.parent.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as directory:
 stage=Path(directory)
 shutil.copytree(ROOT/'hepatogenesis',stage/'hepatogenesis',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 (stage/'__main__.py').write_text('from hepatogenesis.cli import main\nraise SystemExit(main())\n')
 shutil.copy(ROOT/'LICENSE',stage/'LICENSE');shutil.copy(ROOT/'NOTICE',stage/'NOTICE')
 zipapp.create_archive(stage,args.out,interpreter='/usr/bin/env python3',compressed=True)
print(args.out)
