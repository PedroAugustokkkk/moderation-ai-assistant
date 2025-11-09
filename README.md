# 🛡️ SafeView AI - Assistente de Moderação de Risco (v4.2)

> Um protótipo de Computer Vision (CV) que automatiza a moderação de risco, segurança e receita para qualquer plataforma de conteúdo gerado pelo usuário (UGC), marketplace ou rede social.

Este projeto demonstra uma solução de engenharia de nível profissional que vai além da simples moderação de "nudez". Ele é uma ferramenta de **gerenciamento de risco** e **proteção de receita**, projetada para resolver os problemas operacionais centrais de qualquer plataforma que dependa de uploads de usuários.
Caso deseje testar a ferramenta agora, basta acessar a URL: https://moderation-ai.streamlit.app

## 🎯 O Desafio de Negócio

Plataformas de conteúdo UGC vivem um dilema constante:
1.  **Risco Legal (Segurança):** Conteúdo ilegal (violência, armas, drogas) ou que indique coerção (tráfico humano) é um risco jurídico e de marca gigantesco.
2.  **Risco de Receita (Fraude):** Usuários que burlam a plataforma colocando informações de contato (WhatsApp, @) nas imagens para evitar taxas (vazamento de receita).
3.  **Custo Operacional (OPEX):** A necessidade de uma equipe humana cara para filtrar manualmente *milhares* de imagens 24/7, gerando gargalo.
4.  **Calibração:** Como diferenciar conteúdo `adult` (explícito e proibido) de `racy` (sensual ou "limítrofe"), que pode ser permitido dependendo das regras da plataforma?

## 💡 A Solução: Um "Porteiro" Multi-Modelo e Calibrável

O "SafeView AI" não é um "censor" rígido; é um "porteiro" inteligente que usa 4 modelos de IA simultaneamente para tomar uma decisão em 1 segundo:

1.  **Proteção de Receita (OCR):** Lê o texto nas imagens para bloquear números de telefone e @ de redes sociais.
2.  **Proteção de Risco (WAD):** Bloqueia imagens com `armas`, `drogas` ou `álcool` explícito.
3.  **Proteção Humana (Face/Emoção):** Sinaliza imagens onde o rosto detectado apresenta emoções negativas fortes (tristeza, raiva), enviando-as para revisão humana prioritária por suspeita de coerção ou cyberbullying.
4.  **Proteção de Conteúdo (Nudity 2.0):** Bloqueia nudez explícita (`sexual_activity`), com um threshold que pode ser ajustado.

## ✨ Funcionalidades Profissionais

* **Painel de Calibração (Admin):** Esta é a "killer feature". A lógica não é "hardcoded". Um painel na sidebar permite que o time de Produto/Moderação ajuste a *sensibilidade* (o "aperto") de cada filtro (Nudez, Armas, Emoção) em tempo real, sem precisar de um novo deploy de código.
* **Veredito Multi-Violação:** O sistema acumula todas as regras quebradas e apresenta um relatório completo (ex: `REPROVADA: [Contato Detectado, Arma Detectada]`).
* **API Freemium:** Utiliza a stack da **Sightengine**, que não requer cartão de crédito para prototipagem, tornando o projeto 100% acessível.

## 🛠️ Stack de Tecnologia

* **Frontend:** Streamlit
* **Computer Vision API:** Sightengine
* **Modelos Utilizados:** `nudity-2.0`, `wad` (Weapons/Alcohol/Drugs), `text` (OCR), `face-attributes` (Emoção).

## 🚀 Como Executar Localmente

1.  Clone o repositório.
2.  Crie e ative um ambiente virtual (`python -m venv .venv` e `source .venv/bin/activate`).
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  Adquira suas credenciais:
    * Crie uma conta gratuita no [Sightengine.com](https://sightengine.com/).
    * No dashboard, ative os modelos: `nudity-2.0`, `wad`, `text`, `face-attributes`.
    * Pegue seu `API User` e `API Secret`.

5.  Configure suas credenciais (crie este arquivo):

    **Arquivo: `.env`**
    ```plaintext
    SIGHTENGINE_USER="SEU_API_USER_AQUI"
    SIGHTENGINE_SECRET="SEU_API_SECRET_AQUI"
    ```

6.  (Opcional, mas recomendado) Crie um `.gitignore` para proteger seu `.env`.
    ```plaintext
    .venv/
    *.env
    __pycache__/
    ```

7.  Execute a aplicação:
    ```bash
    streamlit run app.py
    ```
