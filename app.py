import json
from pathlib import Path

import streamlit as st

BASE = Path(__file__).parent

st.set_page_config(
    page_title="Idoso Seguro Digital",
    page_icon="🌿",
    layout="centered",
)

st.markdown(
    """
    <style>
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stSidebar"] {
        color: #263C35;
        font-size: 18px;
    }

    p,
    li,
    label,
    [data-testid="stMarkdownContainer"] {
        font-size: 18px;
        line-height: 1.6;
    }

    h1 {
        font-size: 2.5rem;
        line-height: 1.2;
    }

    h2 {
        font-size: 2rem;
        line-height: 1.3;
    }

    h3 {
        font-size: 1.6rem;
        line-height: 1.35;
    }

    [data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-primary"] {
        min-height: 3.25rem;
        padding: 0.65rem 1.25rem;
        font-size: 18px;
    }

    [data-testid="stRadio"] label {
        padding: 0.35rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def carregar_lista_json(nome_arquivo: str, chave_lista: str) -> list[dict]:
    caminho = BASE / nome_arquivo
    try:
        conteudo = caminho.read_text(encoding="utf-8")
        dados = json.loads(conteudo)
    except (
        FileNotFoundError,
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        st.session_state["erro_carregamento_json"] = True
        st.error("Erro ao carregar informações. Tente novamente mais tarde.")
        return []

    registros = dados.get(chave_lista) if isinstance(dados, dict) else None
    if not isinstance(registros, list) or not all(
        isinstance(registro, dict) for registro in registros
    ):
        st.session_state["erro_carregamento_json"] = True
        st.error("Erro ao carregar informações. Tente novamente mais tarde.")
        return []

    if chave_lista == "golpes":
        valido = all(
            isinstance(golpe.get("nome"), str)
            and isinstance(golpe.get("categoria", "Não informada"), str)
            and all(
                isinstance(golpe.get(campo, []), list)
                for campo in ("sinais_alerta", "o_que_fazer", "o_que_nao_fazer")
            )
            for golpe in registros
        )
    else:
        ids = [pergunta.get("id") for pergunta in registros]
        valido = (
            all(
                type(pergunta.get("id")) in (str, int)
                and isinstance(pergunta.get("situacao"), str)
                and isinstance(pergunta.get("opcoes"), list)
                and len(pergunta["opcoes"]) > 0
                and all(isinstance(opcao, str) for opcao in pergunta["opcoes"])
                and type(pergunta.get("correta")) is int
                and 0 <= pergunta["correta"] < len(pergunta["opcoes"])
                and isinstance(pergunta.get("feedback_acerto"), str)
                and isinstance(pergunta.get("feedback_erro"), str)
                for pergunta in registros
            )
            and all(type(pergunta_id) in (str, int) for pergunta_id in ids)
            and len(ids) == len({str(pergunta_id) for pergunta_id in ids})
        )

    if not valido:
        st.session_state["erro_carregamento_json"] = True
        st.error("Erro ao carregar informações. Tente novamente mais tarde.")
        return []

    st.session_state["erro_carregamento_json"] = False
    return registros

def tela_inicial():
    st.image(
        str(BASE / "assets" / "boas-vindas.svg"),
        width="stretch",
    )
    st.title("Idoso Seguro Digital")
    st.write(
        "Este guia reúne orientações sobre golpes comuns contra pessoas "
        "idosas e ajuda você a reconhecer situações de risco."
    )
    st.warning(
        "Este guia é informativo. Ele não substitui a orientação do seu "
        "banco, da polícia ou de órgãos de defesa do consumidor."
    )
    st.write("Use o menu ao lado para navegar entre as seções.")

def tela_golpes():
    st.title("Golpes comuns")
    golpes = carregar_lista_json("golpes.json", "golpes")
    if not golpes:
        if not st.session_state.get("erro_carregamento_json", False):
            st.info("Nenhum golpe cadastrado ainda.")
        return

    categorias = sorted(
        {g.get("categoria", "Não informada") for g in golpes},
        key=str.casefold,
    )
    filtro_categoria = st.selectbox(
        "Filtrar por categoria",
        ["Todas as categorias", *categorias],
        key="filtro_categoria_golpes",
    )
    busca = st.text_input(
        "Buscar por nome ou categoria",
        placeholder="Digite o nome de um golpe ou uma categoria",
        key="busca_golpes",
    ).strip().casefold()

    golpes_filtrados = [
        golpe
        for golpe in golpes
        if (
            filtro_categoria == "Todas as categorias"
            or golpe.get("categoria", "Não informada") == filtro_categoria
        )
        and (
            not busca
            or busca in golpe["nome"].casefold()
            or busca in golpe.get("categoria", "Não informada").casefold()
        )
    ]
    if not golpes_filtrados:
        st.info("Nenhum golpe encontrado com esses filtros.")
        return

    nomes = [g["nome"] for g in golpes_filtrados]
    escolhido = st.selectbox("Escolha um golpe para saber mais", nomes)
    golpe = next(g for g in golpes_filtrados if g["nome"] == escolhido)

    st.subheader(golpe["nome"])
    st.caption(f"Categoria: {golpe.get('categoria', 'Não informada')}")

    st.markdown("**Como acontece**")
    st.write(golpe.get("como_acontece", ""))

    st.markdown("**Sinais de alerta**")
    for s in golpe.get("sinais_alerta", []):
        st.write(f"- {s}")

    st.markdown("**O que fazer**")
    for s in golpe.get("o_que_fazer", []):
        st.write(f"- {s}")

    st.markdown("**O que NÃO fazer**")
    for s in golpe.get("o_que_nao_fazer", []):
        st.write(f"- {s}")

    st.markdown(f"**Onde denunciar:** {golpe.get('onde_denunciar', '')}")
    st.caption(f"Fonte: {golpe.get('fonte', 'Não informada')}")

def tela_quiz():
    st.title("Quiz: você reconhece um golpe?")
    st.write("Responda as perguntas e veja o feedback imediato.")

    perguntas = carregar_lista_json("quiz.json", "perguntas")
    if not perguntas:
        if not st.session_state.get("erro_carregamento_json", False):
            st.info("Nenhuma pergunta cadastrada ainda.")
        return

    st.session_state.setdefault("quiz_indice_pergunta", 0)
    st.session_state.setdefault("quiz_respostas", {})
    st.session_state.setdefault("quiz_finalizado", False)
    respostas = st.session_state.quiz_respostas

    if st.session_state.quiz_finalizado:
        acertos = sum(
            respostas.get(pergunta["id"]) == pergunta["correta"]
            for pergunta in perguntas
        )
        st.subheader("Resultado do quiz")
        st.info(f"Você acertou {acertos} de {len(perguntas)} perguntas.")
        st.subheader("Revisão")
        for pergunta in perguntas:
            acertou = respostas.get(pergunta["id"]) == pergunta["correta"]
            st.markdown(f"**{pergunta['id']}. {pergunta['situacao']}**")
            if acertou:
                st.success(f"Você acertou. {pergunta['feedback_acerto']}")
            else:
                st.error(f"Você errou. {pergunta['feedback_erro']}")
        if st.button("Refazer o quiz", key="quiz_refazer"):
            for pergunta in perguntas:
                st.session_state.pop(f"quiz_resposta_{pergunta['id']}", None)
            st.session_state.quiz_indice_pergunta = 0
            st.session_state.quiz_respostas = {}
            st.session_state.quiz_finalizado = False
            st.rerun()
        return

    indice = min(
        max(st.session_state.quiz_indice_pergunta, 0),
        len(perguntas) - 1,
    )
    pergunta = perguntas[indice]
    st.progress(
        (indice + 1) / len(perguntas),
        text=f"Pergunta {indice + 1} de {len(perguntas)}",
    )
    st.markdown(f"**{pergunta['id']}. {pergunta['situacao']}**")

    resposta_anterior = respostas.get(pergunta["id"])
    opcao = st.radio(
        "Escolha uma opção:",
        pergunta["opcoes"],
        key=f"quiz_resposta_{pergunta['id']}",
        index=resposta_anterior,
    )
    if opcao is not None:
        indice_resposta = pergunta["opcoes"].index(opcao)
        respostas[pergunta["id"]] = indice_resposta
        if indice_resposta == pergunta["correta"]:
            st.success(pergunta["feedback_acerto"])
        else:
            st.error(pergunta["feedback_erro"])

    anterior, avancar = st.columns(2)
    if anterior.button("Anterior", disabled=indice == 0, key="quiz_anterior"):
        st.session_state.quiz_indice_pergunta = indice - 1
        st.rerun()

    ultima_pergunta = indice == len(perguntas) - 1
    if ultima_pergunta:
        if avancar.button(
            "Finalizar",
            disabled=opcao is None,
            type="primary",
            key="quiz_finalizar",
        ):
            st.session_state.quiz_finalizado = True
            st.rerun()
    elif avancar.button(
        "Próxima",
        disabled=opcao is None,
        type="primary",
        key="quiz_proxima",
    ):
        st.session_state.quiz_indice_pergunta = indice + 1
        st.rerun()

def tela_denuncia():
    st.title("Onde procurar ajuda")
    st.write(
        "Se você desconfiar de um golpe ou já tiver sido vítima, procure um "
        "dos canais abaixo."
    )

    st.subheader("Banco")
    st.write(
        "Ligue para o número oficial do seu banco, que aparece no verso do "
        "cartão. Nunca use números recebidos por mensagem."
    )

    st.subheader("Polícia Civil")
    st.write(
        "Registre boletim de ocorrência em uma delegacia ou pelo canal "
        "eletrônico da Polícia Civil do seu estado."
    )

    st.subheader("PROCON")
    st.write(
        "O PROCON orienta consumidores em casos de cobrança indevida ou "
        "suspeita de fraude."
    )

    st.subheader("CERT.br")
    st.write(
        "O CERT.br publica cartilhas de segurança e orienta sobre golpes "
        "digitais."
    )

    st.caption(
        "Este guia não faz denúncias em seu nome. Ele apenas indica canais "
        "oficiais."
    )

def main():
    st.sidebar.title("Menu")
    pagina = st.sidebar.radio(
        "Escolha uma seção",
        ["Início", "Golpes comuns", "Quiz", "Onde procurar ajuda"],
    )

    if pagina == "Início":
        tela_inicial()
    elif pagina == "Golpes comuns":
        tela_golpes()
    elif pagina == "Quiz":
        tela_quiz()
    elif pagina == "Onde procurar ajuda":
        tela_denuncia()

if __name__ == "__main__":
    main()