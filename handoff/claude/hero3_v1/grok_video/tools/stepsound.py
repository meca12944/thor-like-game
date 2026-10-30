# 그록 영상 소리에서 발소리 찾기 (+ 잘라 걸음 소리 만들기)
# 쓰는 법: python3 stepsound.py <영상.mp4> [자를 시작 초들 예 2.0,2.465,2.935,3.395] [출력 폴더] [이름=step_run]
# 1) 소리 꺼내기(모노 48k) 2) 10ms마다 세기 → 바탕의 6배·최고의 25% 넘는 봉우리 = 발소리 3) 간격 → 걸음 빠르기(초·24장 기준 장 수)
# 4) 자르기: 걸음마다 0.28초(0.01초 앞부터), 끝 0.08초 서서히 작게, 최대 0.7, ogg(libvorbis q4)
import sys, os, subprocess, tempfile, wave, numpy as np
mp4 = sys.argv[1]; cuts = [float(v) for v in sys.argv[2].split(',')] if len(sys.argv) > 2 and sys.argv[2] else []
out = sys.argv[3] if len(sys.argv) > 3 else '.'; name = sys.argv[4] if len(sys.argv) > 4 else 'step_run'
wav = os.path.join(tempfile.mkdtemp(), 'a.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp4, '-vn', '-ac', '1', '-ar', '48000', wav], check=True)
w = wave.open(wav); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768; sr = w.getframerate()
hop = sr // 100; e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
base = np.median(e); thr = max(base * 6, e.max() * .25); pk = []
for i in range(1, len(e) - 1):
    if e[i] > thr and e[i] >= e[i - 1] and e[i] >= e[i + 1] and (not pk or i - pk[-1] > 12): pk.append(i)
t = np.array(pk) * .01
print('발소리(초):', np.round(t, 2).tolist())
if len(t) > 2:
    d = np.diff(t); m = float(np.median(d)); print('간격', np.round(d, 2).tolist(), '→ 걸음', round(m, 3), '초 =', round(m * 24, 1), '장(24장/초), 두 걸음', round(m * 48, 1), '장', '· 크기/바탕', round(float(e.max() / base), 1))
os.makedirs(out, exist_ok=True)
for k, c in enumerate(cuts):
    a = int(max(0, c - .01) * sr); seg = x[a:a + int(.28 * sr)].copy(); n = int(.08 * sr)
    seg[-n:] *= np.linspace(1, 0, n)                                   # 끝 0.08초 서서히 작게
    seg *= .7 / max(1e-6, np.abs(seg).max())                            # 최대 0.7
    tmp = os.path.join(os.path.dirname(wav), f'c{k}.wav'); ww = wave.open(tmp, 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(sr)
    ww.writeframes((seg * 32767).astype(np.int16).tobytes()); ww.close()
    o = os.path.join(out, f'{name}_{k + 1}.ogg')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-c:a', 'libvorbis', '-q:a', '4', o], check=True)
    print('잘라 냄', o)
