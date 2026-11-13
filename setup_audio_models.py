"""Download the two public model files once; synthesis then runs offline."""
from pathlib import Path
import urllib.request,hashlib
ROOT=Path(__file__).resolve().parent
BASE='https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/'
FILES={
 'kokoro-v1.0.fp16.onnx':'f3a290d384fbb27966d462905c71a46cef9e5fd00516b40df32a0b4afe77ac96',
 'voices-v1.0.bin':'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d',
}
def sha256(path):
 digest=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
 return digest.hexdigest()
def main():
 dest=ROOT/'models';dest.mkdir(exist_ok=True)
 for name,expected in FILES.items():
  path=dest/name
  if path.exists() and sha256(path)==expected:
   print(name,'already verified');continue
  partial=path.with_suffix(path.suffix+'.part')
  print('Downloading',name,flush=True)
  with urllib.request.urlopen(BASE+name,timeout=60) as response,partial.open('wb') as f:
   while block:=response.read(1024*1024):f.write(block)
  if sha256(partial)!=expected:raise RuntimeError('Checksum mismatch: '+name)
  partial.replace(path);print(name,'verified',flush=True)
if __name__=='__main__':main()