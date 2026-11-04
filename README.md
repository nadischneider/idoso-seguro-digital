# Idoso Seguro Digital

Protótipo de um guia de proteção contra golpes digitais para pessoas idosas.

## Funcionalidades

- Consulta de golpes com busca por nome e filtro por categoria.
- Quiz interativo com uma pergunta por vez, feedback imediato e revisão final.
- Orientações sobre canais oficiais para procurar ajuda.
- Conteúdo local em arquivos JSON; respostas do quiz não são armazenadas.
- Interface com fontes maiores, botões ampliados e cores de alto contraste.

## Como executar

1. Instale o Python 3.10 ou superior.
2. Abra o terminal do VS Code na pasta do projeto.
3. Confira a versão do Python:

   ```powershell
   python --version
   ```

4. Se necessário, instale o Streamlit no mesmo Python:

   ```powershell
   python -m pip install streamlit
   ```

5. Inicie a aplicação:

   ```powershell
   streamlit run app.py
   ```

   Se o comando `streamlit` não for reconhecido, use:

   ```powershell
   python -m streamlit run app.py
   ```

6. Abra o endereço `http://localhost:8501` no navegador. Mantenha o terminal
   aberto enquanto estiver usando a aplicação. Para encerrar, pressione
   `Ctrl+C` no terminal.