
SubProceso Explosion(n)
	Definir i Como Entero
	Para i <- 1 Hasta n Hacer
		Escribir Sin Saltar "*"
	FinPara
	Escribir ""
FinSubProceso


SubProceso ConstruirPeligro(peligro, pasos, cols, nivel)
	Definir t, c Como Entero
	Para t <- 1 Hasta pasos Hacer
		Para c <- 1 Hasta cols Hacer
			Si Aleatorio(1, 100) <= 15 + nivel * 5 Entonces
				peligro[t, c] <- 1000
			SiNo
				peligro[t, c] <- 0
			FinSi
		FinPara
	FinPara
FinSubProceso


Funcion mejor <- PlanRuta(peligro, pasos, cols, inicio)
	Definir costo, padre Como Real
	Dimension costo[6, 10], padre[6, 10]
	Definir t, c, p, mejor, bp Como Entero
	Definir v, b Como Real
	Para c <- 1 Hasta cols Hacer
		costo[1, c] <- 999999
	FinPara
	costo[1, inicio] <- 0
	Para t <- 2 Hasta pasos Hacer
		Para c <- 1 Hasta cols Hacer
			b <- 999999
			bp <- c
			Para p <- c - 2 Hasta c + 2 Hacer
				Si p >= 1 Y p <= cols Entonces
					v <- costo[t - 1, p] + Abs(p - c) * 0.6
					Si v < b Entonces
						b <- v
						bp <- p
					FinSi
				FinSi
			FinPara
			costo[t, c] <- b + peligro[t, c]
			padre[t, c] <- bp
		FinPara
	FinPara
	
	mejor <- inicio
	b <- 999999
	Para c <- 1 Hasta cols Hacer
		Si costo[pasos, c] < b Entonces
			b <- costo[pasos, c]
			mejor <- c
		FinSi
	FinPara
	
	Escribir Sin Saltar "Ruta del autopiloto (columna por paso): "
	c <- mejor
	Para t <- pasos Hasta 2 Con Paso -1 Hacer
		Escribir Sin Saltar c, " <- "
		c <- padre[t, c]
	FinPara
	Escribir c
	Si b >= 1000 Entonces
		mejor <- -1
	FinSi
FinFuncion

// ---------- Premios (drop_reward) ----------
Funcion premio <- SoltarPremio(nivel, esJefe)
	Definir premio Como Entero
	premio <- 0
	Si esJefe Entonces
		premio <- Aleatorio(1, 3)
	SiNo
		Si Aleatorio(1, 100) <= 22 + nivel * 3 Entonces
			Si nivel >= 2 Entonces
				premio <- Aleatorio(1, 3)
			SiNo
				premio <- Aleatorio(2, 3)
			FinSi
		FinSi
	FinSi
FinFuncion

Algoritmo NovaDefender
	Definir vidas, nivel, puntos, opcion, dif, enemigos, bajas, metaBajas Como Entero
	Definir vidaJefe, danio, premio, col, ruta, prob Como Entero
	Definir escudo, multibala, jefeActivo, jugando, pausa Como Logico
	Definir peligro Como Real
	Dimension peligro[6, 10]
	Definir nombreNivel, nombreJefe Como Caracter
	Dimension nombreNivel[3], nombreJefe[3]
	nombreNivel[1] <- "BASICO"
	nombreNivel[2] <- "INTERMEDIO"
	nombreNivel[3] <- "DIFICIL"
	nombreJefe[1] <- "JEFE AMARILLO"
	nombreJefe[2] <- "JEFE ROJO"
	nombreJefe[3] <- "JEFE NEGRO DE OJOS ROJOS"

	
	Escribir "=============================="
	Escribir "        NOVA DEFENDER"
	Escribir "=============================="
	Escribir "1. START   0. SALIR"
	Leer opcion
	Si opcion <> 1 Entonces
		Escribir "Hasta pronto."
	SiNo
		Escribir "Dificultad: 1 Basico  2 Intermedio  3 Dificil"
		Leer dif
		Si dif < 1 O dif > 3 Entonces
			dif <- 2
		FinSi
		vidas <- 3
		nivel <- 1
		puntos <- 0
		escudo <- Falso
		multibala <- Falso
		jugando <- Verdadero
		col <- 5

		Mientras jugando Y nivel <= 3 Hacer
			Escribir ""
			Escribir "===== NIVEL ", nivel, " - ", nombreNivel[nivel], " ====="
			bajas <- 0
			metaBajas <- 4 + nivel * 2
			jefeActivo <- Falso
			vidaJefe <- 0

			Mientras jugando Y (bajas < metaBajas O jefeActivo) Hacer
				Si bajas >= metaBajas Y No jefeActivo Y vidaJefe = 0 Entonces
					jefeActivo <- Verdadero
					vidaJefe <- 8 + nivel * 4 + dif * 2
					Escribir "!!! ALERTA: aparece el ", nombreJefe[nivel], " !!!"
				FinSi
				Si jefeActivo Entonces
					Escribir "Jefe: ", vidaJefe, " PV"
				SiNo
					Escribir "Enemigos y meteoritos se acercan... (bajas ", bajas, "/", metaBajas, ")"
				FinSi
				Escribir "Vidas: ", vidas, "  Puntos: ", puntos, "  Escudo: ", escudo, "  Multibala: ", multibala
				Escribir "1 Disparar  2 Esquivar  3 Autopiloto  4 Pausa  0 Salir"
				Leer opcion

				Si opcion = 4 Entonces
					
					pausa <- Verdadero
					Mientras pausa Hacer
						Escribir "== PAUSA == (musica detenida)"
						Escribir "1 Continuar  2 Salir al inicio"
						Leer opcion
						Si opcion = 2 Entonces
							jugando <- Falso
						FinSi
						pausa <- Falso
					FinMientras
					Si jugando Entonces
						Escribir "Musica reanudada."
					FinSi
				SiNo
					Si opcion = 0 Entonces
						jugando <- Falso
					SiNo
						prob <- 30 + nivel * 8 + dif * 4
						Si opcion = 1 Entonces
							danio <- 1
							Si multibala Entonces
								danio <- 3
							FinSi
							Si jefeActivo Entonces
								vidaJefe <- vidaJefe - danio
								Escribir "Impacto al jefe: -", danio
								Si vidaJefe <= 0 Entonces
									Escribir "JEFE DESTRUIDO!"
									Explosion(20)
									puntos <- puntos + 500 * nivel
									jefeActivo <- Falso
									vidaJefe <- -1
									premio <- SoltarPremio(nivel, Verdadero)
								SiNo
									premio <- 0
								FinSi
							SiNo
								bajas <- bajas + danio
								puntos <- puntos + 100 * danio
								Escribir "Enemigo destruido!"
								Explosion(8)
								premio <- SoltarPremio(nivel, Falso)
							FinSi
							Segun premio Hacer
								1: vidas <- vidas + 1
									Escribir "Premio: VIDA EXTRA (corazon)"
								2: escudo <- Verdadero
									Escribir "Premio: ESCUDO"
								3: multibala <- Verdadero
									Escribir "Premio: MULTIBALA"
							FinSegun
						SiNo
							Si opcion = 2 Entonces
								prob <- prob - 20
							SiNo
								ConstruirPeligro(peligro, 5, 10, nivel)
								ruta <- PlanRuta(peligro, 5, 10, col)
								Si ruta > 0 Entonces
									col <- ruta
									prob <- 0
									Escribir "Autopiloto: ruta segura encontrada."
								SiNo
									Escribir "Autopiloto: no hay ruta totalmente segura."
								FinSi
							FinSi
						FinSi
						
						Si Aleatorio(1, 100) <= prob Entonces
							Si escudo Entonces
								escudo <- Falso
								Escribir "El escudo bloqueo el impacto."
							SiNo
								vidas <- vidas - 1
								multibala <- Falso
								Escribir "Te golpearon! Pierdes una vida."
								Explosion(5)
							FinSi
						FinSi
						Si vidas <= 0 Entonces
							jugando <- Falso
							Escribir "GAME OVER. Puntos: ", puntos
						FinSi
					FinSi
				FinSi
			FinMientras
			Si jugando Entonces
				nivel <- nivel + 1
			FinSi
		FinMientras
		Si nivel > 3 Entonces
			Escribir "VICTORIA! Salvaste la galaxia. Puntos: ", puntos
		FinSi
	FinSi
FinAlgoritmo
