# Defensor Galáctico — Programación Dinámica (Python + Pygame y HTML)

Juego de naves espaciales desarrollado para el proyecto de **Análisis de Algoritmos**. La ruta óptima de evasión y ataque del autopiloto (tecla **T**) se calcula en tiempo real mediante **Programación Dinámica** (enfoque *bottom-up*).

El repositorio incluye **dos versiones** jugables:

| Versión | Cómo ejecutarla |
|---|---|
| **Pygame** (`main.py`) | Ejecutar `pip install -r requirements.txt` y luego `python main.py` |
| **Web** (`index.html`) | Abrir `index.html` directamente en cualquier navegador (Chrome/Edge) o desplegar con GitHub Pages (`.github/workflows/pages.yml`) |

---

## Reglas y Mecánicas del Juego

- **Sistema de supervivencia:** 3 vidas por partida.
- **Progresión en 3 niveles:**
  1. **Básico:** Enemigos a velocidad media.
  2. **Intermedio:** Enemigos rápidos con mayor cadencia.
  3. **Difícil:** Enemigos rápidos + lluvia de meteoritos.
- **Combate:** Tanto la nave del jugador como los enemigos disparan proyectiles. Al finalizar cada nivel aparece un **Jefe Final** con ataques de ráfaga y rayo láser.
- **Controles:**
  - `Flechas` / `WASD` / `Mouse`: Mover la nave.
  - `ESPACIO` / `Clic izquierdo`: Disparar.
  - `T`: Activar / desactivar el **Autopiloto (PD)**.
  - `F`: Mostrar / ocultar métricas de tiempo por fotograma (ms/frame).
  - `ESC`: Pausar el juego.

---

## Implementación de Programación Dinámica

La lógica algorítmica reside en la función `plan_route()` dentro de `main.py` (y su equivalente en `index.html`):

- **Estructura:** Se construye una matriz de estados `dp[t][c]` que almacena el costo mínimo acumulado (peligro por proyectiles, enemigos y meteoritos) para posicionar la nave en la columna `c` durante el paso de tiempo futuro `t`.
- **Complejidad:** Cada subproblema se evalúa una única vez de forma iterativa (**sin recursividad**), garantizando una complejidad temporal de **$O(n \times m)$**, donde $n$ es el horizonte de pasos futuros y $m$ el número de columnas discretizadas de la pantalla.
- **Alcance:** El motor gráfico, colisiones y físicas funcionan de manera convencional; la Programación Dinámica gobierna exclusivamente la toma de decisiones del autopiloto.

---

## Análisis Empírico

Para evaluar el rendimiento y validar la eficiencia temporal del algoritmo frente a distintos tamaños de entrada, ejecuta el script de pruebas:

```bash
python benchmark_dinamica.py
