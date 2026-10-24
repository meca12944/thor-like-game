# 멈춘 그림 다시: 실패하면 3번까지
for k in "$@"; do for t in 1 2 3; do python3 gen5.py $k > log_$k.txt 2>&1 && break; done; done
