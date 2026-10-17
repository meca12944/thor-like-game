# take.py name1_view name2_view ... : copies newest len(args) attachments in mtime order
import os, sys, shutil
A='/cursor/stores/store-795156a0-7465-4f60-aac0-5ea8cd38a231/grok-bot/agents/4fedc784-0420-4bf1-b51b-e98cbd24f667/attachments/'
fs=sorted(os.listdir(A), key=lambda f: os.path.getmtime(A+f))[-len(sys.argv[1:]):]
for f,n in zip(fs,sys.argv[1:]):
    if n!='-': shutil.copy(A+f, f'/workspace/town-demo/style_sample/src/fem_walk/{n}.jpg'); print(f[:8],'->',n)
