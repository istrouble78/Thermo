#!/usr/bin/env python3
"""
Lotofácil - Download automático do histórico e análise estatística.

Baixa (com cache local incremental) todos os concursos já sorteados da
Lotofácil diretamente da API oficial da Caixa Econômica Federal, faz uma
análise estatística do histórico (frequência, atraso, pares, paridade,
soma das dezenas, repetição entre concursos, distribuição por coluna da
cartela) e sugere um jogo para o próximo concurso com base nesses critérios.

IMPORTANTE: a Lotofácil é um sorteio aleatório. Concursos passados não
influenciam concursos futuros. Nenhuma análise estatística garante ou
aumenta comprovadamente a chance de acerto - esta ferramenta tem fins
exploratórios/educacionais.

Uso:
    python lotofacil_analise.py
    python lotofacil_analise.py --forcar-download
    python lotofacil_analise.py --apenas-ultimos 300 --saida relatorio.txt
"""

import argparse
import csv
import statistics
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import combinations
from pathlib import Path

import requests

API_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
FALLBACK_BULK_URL = "https://loteriascaixa-api.herokuapp.com/api/lotofacil"
CACHE_FILE = Path(__file__).with_name("lotofacil_historico.csv")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LotofacilAnalise/1.0)"}

TOTAL_DEZENAS = 25
DEZENAS_POR_JOGO = 15  # dezenas sorteadas em cada concurso
MIN_DEZENAS_APOSTA = 15
MAX_DEZENAS_APOSTA = 20  # a Lotofácil aceita apostas de 15 a 20 números

# Layout da cartela oficial da Lotofácil (5 colunas x 5 linhas)
COLUNAS_CARTELA = {
    1: [1, 6, 11, 16, 21],
    2: [2, 7, 12, 17, 22],
    3: [3, 8, 13, 18, 23],
    4: [4, 9, 14, 19, 24],
    5: [5, 10, 15, 20, 25],
}


# --------------------------------------------------------------------------
# Download e cache do histórico
# --------------------------------------------------------------------------

def buscar_concurso(session, numero=None, retries=3, timeout=10):
    """Busca um concurso específico (ou o mais recente, se numero=None)."""
    url = API_BASE if numero is None else f"{API_BASE}/{numero}"
    ultimo_erro = None
    for tentativa in range(1, retries + 1):
        try:
            resp = session.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as exc:
            ultimo_erro = exc
            if tentativa < retries:
                time.sleep(1.5 * tentativa)
    raise ultimo_erro


def descobrir_ultimo_concurso(session):
    dados = buscar_concurso(session)
    return int(dados["numero"])


def parse_concurso(dados):
    numero = int(dados["numero"])
    data = dados.get("dataApuracao", "")
    dezenas = sorted(int(d) for d in dados["listaDezenas"])
    if len(dezenas) != DEZENAS_POR_JOGO:
        raise ValueError(f"Concurso {numero} com número inesperado de dezenas: {dezenas}")
    return numero, data, dezenas


def baixar_fallback_bulk(session, timeout=30):
    """Fonte alternativa: baixa todo o histórico em uma única requisição."""
    resp = session.get(FALLBACK_BULK_URL, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    dados = resp.json()
    historico = {}
    for item in dados:
        numero = int(item["concurso"])
        data = item.get("data", "")
        dezenas = sorted(int(d) for d in item["dezenas"])
        historico[numero] = (data, dezenas)
    return historico


def carregar_cache():
    historico = {}
    if CACHE_FILE.exists():
        with CACHE_FILE.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # cabeçalho
            for linha in reader:
                if not linha:
                    continue
                numero = int(linha[0])
                data = linha[1]
                dezenas = sorted(int(x) for x in linha[2:2 + DEZENAS_POR_JOGO])
                historico[numero] = (data, dezenas)
    return historico


def salvar_cache(historico):
    with CACHE_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["concurso", "data"] + [f"dezena_{i + 1}" for i in range(DEZENAS_POR_JOGO)])
        for numero in sorted(historico):
            data, dezenas = historico[numero]
            writer.writerow([numero, data] + dezenas)


def atualizar_historico(max_workers=12, forcar=False, apenas_ultimos=None):
    """Garante que o cache local tenha todo o histórico (ou os N mais recentes)."""
    historico = {} if forcar else carregar_cache()

    with requests.Session() as session:
        try:
            ultimo = descobrir_ultimo_concurso(session)
        except Exception as exc:
            print(f"Não foi possível acessar a API oficial da Caixa ({exc}).")
            print("Tentando fonte alternativa (API pública com histórico completo)...")
            historico_fallback = baixar_fallback_bulk(session)
            historico.update(historico_fallback)
            salvar_cache(historico)
            print(f"Histórico obtido via fonte alternativa: {len(historico)} concursos.")
            return historico

        primeiro_desejado = 1
        if apenas_ultimos:
            primeiro_desejado = max(1, ultimo - apenas_ultimos + 1)

        faltantes = [n for n in range(primeiro_desejado, ultimo + 1) if n not in historico]

        if not faltantes:
            print(f"Histórico já atualizado: {len(historico)} concursos em cache (último: {ultimo}).")
            return historico

        print(f"Baixando {len(faltantes)} concurso(s) novo(s) (até o concurso {ultimo})...")

        falhas = []
        concluidos = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = {executor.submit(buscar_concurso, session, n): n for n in faltantes}
            for futuro in as_completed(futuros):
                numero_alvo = futuros[futuro]
                concluidos += 1
                try:
                    dados = futuro.result()
                    numero, data, dezenas = parse_concurso(dados)
                    historico[numero] = (data, dezenas)
                except Exception:
                    falhas.append(numero_alvo)

                if concluidos % 200 == 0 or concluidos == len(faltantes):
                    print(f"  ... {concluidos}/{len(faltantes)} baixados")

        if falhas:
            amostra = sorted(falhas)[:10]
            sufixo = "..." if len(falhas) > 10 else ""
            print(f"Aviso: {len(falhas)} concurso(s) não puderam ser baixados: {amostra}{sufixo}")

        salvar_cache(historico)
        print(f"Histórico salvo em '{CACHE_FILE.name}': {len(historico)} concursos.")

    return historico


def historico_ordenado(historico, apenas_ultimos=None):
    numeros = sorted(historico)
    if apenas_ultimos:
        numeros = numeros[-apenas_ultimos:]
    return [(n, historico[n][0], historico[n][1]) for n in numeros]


# --------------------------------------------------------------------------
# Análise estatística
# --------------------------------------------------------------------------

def analisar(lista_concursos, janela_recente=25):
    todos_jogos = [dezenas for _, _, dezenas in lista_concursos]
    total_concursos = len(todos_jogos)

    freq_total = Counter()
    for jogo in todos_jogos:
        freq_total.update(jogo)

    recentes = todos_jogos[-janela_recente:] if total_concursos >= janela_recente else todos_jogos
    freq_recente = Counter()
    for jogo in recentes:
        freq_recente.update(jogo)

    atraso = {}
    for dezena in range(1, TOTAL_DEZENAS + 1):
        contador = 0
        for jogo in reversed(todos_jogos):
            if dezena in jogo:
                atraso[dezena] = contador
                break
            contador += 1
        else:
            atraso[dezena] = total_concursos

    pares = Counter()
    for jogo in todos_jogos:
        pares.update(combinations(sorted(jogo), 2))

    contagem_pares_impares = Counter()
    for jogo in todos_jogos:
        n_pares = sum(1 for d in jogo if d % 2 == 0)
        contagem_pares_impares[n_pares] += 1

    somas = [sum(jogo) for jogo in todos_jogos]
    soma_media = statistics.mean(somas) if somas else 0
    soma_desvio = statistics.pstdev(somas) if len(somas) > 1 else 0

    repeticoes = [
        len(set(anterior) & set(atual))
        for anterior, atual in zip(todos_jogos, todos_jogos[1:])
    ]
    repeticao_media = statistics.mean(repeticoes) if repeticoes else 0

    freq_coluna = Counter()
    for jogo in todos_jogos:
        for dezena in jogo:
            for coluna, dezenas_coluna in COLUNAS_CARTELA.items():
                if dezena in dezenas_coluna:
                    freq_coluna[coluna] += 1
                    break

    return {
        "total_concursos": total_concursos,
        "janela_recente": janela_recente,
        "freq_total": freq_total,
        "freq_recente": freq_recente,
        "atraso": atraso,
        "pares": pares,
        "contagem_pares_impares": contagem_pares_impares,
        "somas": somas,
        "soma_media": soma_media,
        "soma_desvio": soma_desvio,
        "repeticao_media": repeticao_media,
        "freq_coluna": freq_coluna,
    }


# --------------------------------------------------------------------------
# Geração da sugestão de jogo
# --------------------------------------------------------------------------

def _sugestao_combinada(resultado, pesos=(0.35, 0.45, 0.20), quantidade=DEZENAS_POR_JOGO):
    """Combina frequência histórica, tendência recente e atraso em um score
    por dezena. Monta um núcleo de 15 dezenas ajustado pela soma histórica
    e, se a aposta pedida tiver mais de 15 números (desdobramento de 16 a
    20 dezenas, como a Lotofácil permite), completa com as próximas
    melhores dezenas do ranking."""
    freq_total = resultado["freq_total"]
    freq_recente = resultado["freq_recente"]
    atraso = resultado["atraso"]

    max_freq_total = max(freq_total.values()) if freq_total else 1
    max_freq_recente = max(freq_recente.values()) if freq_recente else 1
    max_atraso = max(atraso.values()) if atraso else 1

    w_total, w_recente, w_atraso = pesos
    pontuacao = {}
    for dezena in range(1, TOTAL_DEZENAS + 1):
        score = (
            w_total * (freq_total.get(dezena, 0) / max_freq_total)
            + w_recente * (freq_recente.get(dezena, 0) / max_freq_recente)
            + w_atraso * (atraso.get(dezena, 0) / max_atraso)
        )
        pontuacao[dezena] = score

    ranking = sorted(pontuacao, key=lambda d: pontuacao[d], reverse=True)

    nucleo = _ajustar_soma(
        ranking[:DEZENAS_POR_JOGO], ranking, resultado["soma_media"], resultado["soma_desvio"]
    )

    if quantidade > DEZENAS_POR_JOGO:
        extras = [d for d in ranking if d not in nucleo][: quantidade - DEZENAS_POR_JOGO]
        sugestao = nucleo + extras
    else:
        sugestao = nucleo[:quantidade]

    return sorted(sugestao), pontuacao


def _ajustar_soma(sugestao, ranking, media_soma, desvio_soma, max_iter=40):
    """Troca dezenas da seleção por reservas sempre que a soma total sair da
    faixa média +/- 1 desvio padrão do histórico. A cada iteração, entre
    todas as trocas (membro da seleção <-> reserva) que aproximam a soma da
    média, prioriza-se remover o membro pior rankeado. Uma troca só é
    aplicada se reduzir estritamente a distância até a média, o que garante
    que o processo sempre termina (não há como oscilar indefinidamente)."""
    if desvio_soma <= 0:
        return list(sugestao)

    faixa_min, faixa_max = media_soma - desvio_soma, media_soma + desvio_soma
    sugestao = list(sugestao)
    reserva = [d for d in ranking if d not in sugestao]

    for _ in range(max_iter):
        soma_atual = sum(sugestao)
        if faixa_min <= soma_atual <= faixa_max:
            break

        diferenca_atual = abs(soma_atual - media_soma)
        melhor_swap = None

        # avalia os membros do pior para o melhor rankeado, aceitando a
        # primeira troca que melhore a distância até a média
        for membro in sorted(sugestao, key=lambda d: -ranking.index(d)):
            candidatos_bons = [
                c for c in reserva
                if abs((soma_atual - membro + c) - media_soma) < diferenca_atual
            ]
            if candidatos_bons:
                melhor_candidato = min(
                    candidatos_bons,
                    key=lambda c: abs((soma_atual - membro + c) - media_soma),
                )
                melhor_swap = (membro, melhor_candidato)
                break

        if melhor_swap is None:
            break  # nenhuma troca melhora a soma; evita loop sem progresso

        membro, candidato = melhor_swap
        sugestao.remove(membro)
        sugestao.append(candidato)
        reserva.remove(candidato)
        reserva.append(membro)

    return sugestao


def gerar_sugestoes(resultado, quantidade=DEZENAS_POR_JOGO):
    ranking_total = [d for d, _ in resultado["freq_total"].most_common(TOTAL_DEZENAS)]
    ranking_recente = [d for d, _ in resultado["freq_recente"].most_common(TOTAL_DEZENAS)]
    ranking_atraso = sorted(
        range(1, TOTAL_DEZENAS + 1), key=lambda d: -resultado["atraso"].get(d, 0)
    )

    sugestao_principal, pontuacao = _sugestao_combinada(resultado, quantidade=quantidade)

    alternativas = {
        "Mais quentes (frequência histórica)": sorted(ranking_total[:quantidade]),
        "Tendência recente": sorted(ranking_recente[:quantidade]),
        "Números atrasados": sorted(ranking_atraso[:quantidade]),
    }

    return sugestao_principal, pontuacao, alternativas


# --------------------------------------------------------------------------
# Relatório
# --------------------------------------------------------------------------

def montar_relatorio(resultado, lista_concursos, quantidade=DEZENAS_POR_JOGO):
    total = resultado["total_concursos"]
    janela_recente = resultado["janela_recente"]
    primeiro, ultimo = lista_concursos[0][0], lista_concursos[-1][0]
    data_ultimo = lista_concursos[-1][1]

    linhas = []
    linhas.append(
        f"\nConcursos analisados: {total} (do {primeiro} ao {ultimo}, "
        f"último sorteio em {data_ultimo})"
    )

    linhas.append("\n--- NÚMEROS MAIS FREQUENTES (histórico completo) ---")
    for dezena, qtd in resultado["freq_total"].most_common(10):
        linhas.append(f"  {dezena:02d} -> saiu {qtd} vezes ({100 * qtd / total:.1f}%)")

    linhas.append("\n--- NÚMEROS MENOS FREQUENTES (histórico completo) ---")
    for dezena, qtd in sorted(resultado["freq_total"].items(), key=lambda x: x[1])[:10]:
        linhas.append(f"  {dezena:02d} -> saiu {qtd} vezes ({100 * qtd / total:.1f}%)")

    linhas.append(f"\n--- TENDÊNCIA RECENTE (últimos {janela_recente} concursos) ---")
    for dezena, qtd in resultado["freq_recente"].most_common(10):
        linhas.append(f"  {dezena:02d} -> saiu {qtd}x nos últimos {janela_recente}")

    linhas.append("\n--- NÚMEROS MAIS ATRASADOS (há mais tempo sem sair) ---")
    for dezena, atraso in sorted(resultado["atraso"].items(), key=lambda x: -x[1])[:10]:
        linhas.append(f"  {dezena:02d} -> {atraso} concurso(s) sem sair")

    linhas.append("\n--- PARES DE NÚMEROS QUE MAIS SAEM JUNTOS ---")
    for (a, b), qtd in resultado["pares"].most_common(10):
        linhas.append(f"  {a:02d} e {b:02d} -> juntos em {qtd} concursos")

    linhas.append("\n--- DISTRIBUIÇÃO PARES x ÍMPARES POR JOGO ---")
    for n_pares, qtd in sorted(resultado["contagem_pares_impares"].items()):
        linhas.append(f"  {n_pares} pares / {15 - n_pares} ímpares -> {qtd} concurso(s)")

    linhas.append("\n--- SOMA DAS 15 DEZENAS SORTEADAS ---")
    linhas.append(
        f"  Média histórica: {resultado['soma_media']:.1f}  |  "
        f"Desvio padrão: {resultado['soma_desvio']:.1f}"
    )

    linhas.append("\n--- REPETIÇÃO EM RELAÇÃO AO CONCURSO ANTERIOR ---")
    linhas.append(
        f"  Em média, {resultado['repeticao_media']:.1f} dezenas se repetem "
        "de um concurso para o seguinte."
    )

    linhas.append("\n--- DISTRIBUIÇÃO POR COLUNA DA CARTELA OFICIAL ---")
    for coluna, qtd in sorted(resultado["freq_coluna"].items()):
        linhas.append(f"  Coluna {coluna} {COLUNAS_CARTELA[coluna]} -> {qtd} ocorrências")

    sugestao, _pontuacao, alternativas = gerar_sugestoes(resultado, quantidade=quantidade)

    linhas.append("\n" + "=" * 70)
    linhas.append(f"SUGESTÃO PRINCIPAL PARA O PRÓXIMO CONCURSO ({quantidade} números)")
    linhas.append("=" * 70)
    linhas.append(f"  {' - '.join(f'{d:02d}' for d in sugestao)}")
    n_pares_sug = sum(1 for d in sugestao if d % 2 == 0)
    linhas.append(
        f"  Soma: {sum(sugestao)}  |  Pares: {n_pares_sug}  |  "
        f"Ímpares: {quantidade - n_pares_sug}"
    )
    linhas.append(
        "  Critério: as 15 dezenas centrais combinam frequência histórica,\n"
        "  tendência recente e atraso, com ajuste para manter a soma dentro da\n"
        "  faixa mais comum no histórico (média +/- 1 desvio padrão)."
        + (
            f"\n  As {quantidade - DEZENAS_POR_JOGO} dezena(s) extra(s) são as próximas"
            " melhor rankeadas pelo mesmo score."
            if quantidade > DEZENAS_POR_JOGO
            else ""
        )
    )

    linhas.append("\n--- OUTRAS SUGESTÕES (estratégias alternativas para comparação) ---")
    for nome, jogo in alternativas.items():
        linhas.append(f"  {nome}: {' - '.join(f'{d:02d}' for d in jogo)}  (soma {sum(jogo)})")

    linhas.append("\n" + "=" * 70)
    linhas.append("AVISO IMPORTANTE")
    linhas.append("=" * 70)
    linhas.append(
        "A Lotofácil é um sorteio aleatório: cada concurso é um evento independente\n"
        "e o resultado de concursos passados NÃO influencia o próximo sorteio.\n"
        "Nenhum método estatístico garante ou comprovadamente aumenta a chance de\n"
        "acerto. Esta análise é uma ferramenta exploratória/educacional para\n"
        "observar padrões históricos (frequência, atraso, soma, paridade). Jogue\n"
        "com responsabilidade."
    )

    return "\n".join(linhas)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Baixa automaticamente o histórico da Lotofácil e sugere um jogo "
            "para o próximo concurso com base em análise estatística."
        )
    )
    parser.add_argument(
        "--forcar-download", action="store_true",
        help="Ignora o cache local e baixa todo o histórico novamente."
    )
    parser.add_argument(
        "--workers", type=int, default=12,
        help="Número de downloads simultâneos (padrão: 12)."
    )
    parser.add_argument(
        "--janela-recente", type=int, default=25,
        help="Quantidade de concursos recentes usados na análise de tendência (padrão: 25)."
    )
    parser.add_argument(
        "--apenas-ultimos", type=int, default=None,
        help="Baixa/analisa apenas os N concursos mais recentes (útil para testes rápidos)."
    )
    parser.add_argument(
        "--saida", type=str, default=None,
        help="Caminho de um arquivo .txt para salvar o relatório completo."
    )
    parser.add_argument(
        "--quantidade", type=int, default=DEZENAS_POR_JOGO,
        help=(
            "Quantidade de números na aposta sugerida, de "
            f"{MIN_DEZENAS_APOSTA} a {MAX_DEZENAS_APOSTA} (padrão: {DEZENAS_POR_JOGO}), "
            "conforme os desdobramentos aceitos pela Lotofácil."
        )
    )
    args = parser.parse_args()

    if not MIN_DEZENAS_APOSTA <= args.quantidade <= MAX_DEZENAS_APOSTA:
        parser.error(
            f"--quantidade deve estar entre {MIN_DEZENAS_APOSTA} e {MAX_DEZENAS_APOSTA}."
        )

    print("=" * 70)
    print("LOTOFÁCIL - ANÁLISE ESTATÍSTICA DO HISTÓRICO E SUGESTÃO DE JOGO")
    print("=" * 70)

    historico = atualizar_historico(
        max_workers=args.workers,
        forcar=args.forcar_download,
        apenas_ultimos=args.apenas_ultimos,
    )
    lista = historico_ordenado(historico, apenas_ultimos=args.apenas_ultimos)

    if len(lista) < 10:
        print("Histórico insuficiente para uma análise confiável.")
        return

    resultado = analisar(lista, janela_recente=args.janela_recente)
    relatorio = montar_relatorio(resultado, lista, quantidade=args.quantidade)

    print(relatorio)

    if args.saida:
        Path(args.saida).write_text(relatorio, encoding="utf-8")
        print(f"\nRelatório salvo em: {args.saida}")


if __name__ == "__main__":
    main()
