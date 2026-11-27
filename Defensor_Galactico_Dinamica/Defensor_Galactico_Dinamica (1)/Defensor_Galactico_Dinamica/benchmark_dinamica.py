"""
Analisis empirico: PROGRAMACION DINAMICA (version Defensor Galactico)
Problema de la nave: elegir la ruta (una columna por paso) que evita
naves, meteoritos y balas durante n pasos, moviendose -1, 0 o +1 columnas.

Ambos algoritmos usan EXACTAMENTE la misma tabla de peligro y el mismo modelo,
por eso deben devolver el mismo costo optimo (se verifica en cada fila).

  Recursividad:          O(3^n)      (re-calcula los mismos subproblemas)
  Programacion dinamica: O(n * m)    (cada subproblema (t, columna) una sola vez)

Uso:   python benchmark.py            (no necesita pygame)
Salida: tabla en pantalla + resultados_benchmark.csv
"""
import csv
import random
import statistics
import time

COLS = 36            # columnas de la rejilla
MOVES = (-1, 0, 1)   # movimientos por paso
MOVE_COST = 0.6
HARD = 1000.0
INF = float("inf")
BUDGET_MS = 1000 / 60    # 16,7 ms por fotograma a 60 FPS


def make_danger(n, seed):
    """Tabla peligro[t][c]: 6 'obstaculos' por paso, cada uno bloquea 3 columnas."""
    rnd = random.Random(seed)
    danger = [[0.0] * COLS for _ in range(n + 1)]
    for t in range(1, n + 1):
        for _ in range(6):
            c = rnd.randint(1, COLS - 2)
            for k in (c - 1, c, c + 1):
                danger[t][k] = HARD
    return danger


# -------------------------------------------------------- PROGRAMACION DINAMICA
def route_dp(c0, n, danger):
    """dp[t][c] = danger[t][c] + min_p(dp[t-1][p] + MOVE_COST*|p-c|)."""
    prev = [INF] * COLS
    prev[c0] = 0.0
    for t in range(1, n + 1):
        cur = [INF] * COLS
        row = danger[t]
        for c in range(COLS):
            best = INF
            for dc in MOVES:
                p = c + dc
                if 0 <= p < COLS:
                    v = prev[p] + abs(dc) * MOVE_COST
                    if v < best:
                        best = v
            if best < INF:
                cur[c] = best + row[c]
        prev = cur
    return min(prev)


def timeit(fn, reps):
    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        result = fn()
        times.append((time.perf_counter() - t0) * 1000)
    return statistics.median(times), result



def main():
    start_col = COLS // 2
    rows = []
    print(f"{'n':>3} {'n*m':>7} {'DP ms':>9} {'< 16.7 ms':>10}")
    for n in (3, 5, 8, 10, 13, 20, 30, 60, 100):
        danger = make_danger(n, seed=n)
        t_dp, _ = timeit(lambda: route_dp(start_col, n, danger), 200)
        rows.append([n, n * COLS, round(t_dp, 4), t_dp < BUDGET_MS])
        print(f"{n:>3} {n * COLS:>7} {t_dp:>9.4f} {str(t_dp < BUDGET_MS):>10}")
    with open("resultados_dinamica.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n_pasos", "n*m", "dp_ms", "menor_16.7ms"])
        w.writerows(rows)
    print("\nGuardado: resultados_dinamica.csv (presupuesto: %.1f ms)" % BUDGET_MS)


if __name__ == "__main__":
    main()
