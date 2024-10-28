# Nome da Solução
OrderAI

## Integrantes do Grupo

- Gabriel Augusto Fernandes - RM98986

- Kauê Fernandes Braz - RM97768

- Mariana Trentino Albano - RM551154

- Matheus Dantas de Sousa - RM98406

- Thomas Nícolas de Melo Mendonça - RM99832

## Nossa Solução

Nossa solução consiste em um sistema abrangente baseado em **IA generativa** e **Deep Analytics**. O objetivo é transformar a experiência do usuário por meio de inovações tecnológicas que otimizem o processo de compra e recomendação de produtos.

### 1. Assistente por Voz (Anotação de Pedidos)

Desenvolvemos um **assistente por voz** com processamento de linguagem natural, capaz de interagir com o cliente de forma humanizada e registrar pedidos de maneira precisa. Este assistente tem o foco na **acessibilidade**, facilitando a experiência de usuários com **deficiência visual**. 

Com mais de **6,5 milhões de deficientes visuais no Brasil**, essa solução promove inclusão e também atrai outros públicos ao oferecer uma maneira rápida e eficiente de realizar pedidos. Além de acessibilidade, o assistente por voz é um **otimizador de tempo**, agilizando o processo de compra para todos os clientes.

**Benefícios do Assistente por Voz:**
- Inclusão de pessoas com deficiência visual.
- Agilidade e facilidade no registro de pedidos.
- Atração de novos públicos, devido à conveniência oferecida.

### 2. Sistema de Recomendação

O **sistema de recomendação** utiliza a própria IA Generativa para analisar tendências de compras e trazer recomendações em cima do produto que está sendo comproado no momento. A partir disso, ele sugere produtos complementares ou realiza comparações entre os produtos.
O sistema de recomendação poderá ser utilizado de duas maneiras:
1. **Assistente Virtual**: O assistente por voz também poderá oferecer recomendações personalizadas durante as interações.
2. **Interface Visual**: Um layout visual com sugestões de produtos complementares será disponibilizado na plataforma, proporcionando uma experiência personalizada ao cliente.

**Benefícios do Sistema de Recomendação:**
- Sugerir produtos complementares para aumentar a satisfação do cliente.
- Analisar padrões de comportamento e dados sazonais para recomendações mais precisas.
- Melhoria na experiência de compra e maior potencial de vendas.

---

A combinação dessas duas tecnologias resulta em uma solução completa e personalizada, que promove acessibilidade, praticidade e melhora a interação entre o cliente e a plataforma de vendas.

## Arquitetura da IA Utilizada

### Descrição da Arquitetura

Nossa solução é composta por duas camadas principais de IA, cada uma abordando diferentes aspectos do assistente por voz e do sistema de recomendação:

1. **Assistente por Voz (Anotação de Pedidos):**
   - **Reconhecimento de Fala:** Utiliza a biblioteca `speech_recognition` para converter a fala em texto no FrontEnd. Este componente capta o comando do usuário através do microfone e transcreve para um formato processável pela IA.
   - **Processamento de Linguagem Natural (PLN):** O texto transcrito é processado pelo modelo de IA generativa, Gemini, para entender e gerar respostas contextuais e humanizadas.
   - **Síntese de Fala:** A resposta gerada pelo modelo é convertida novamente em fala usando a biblioteca `responsiveVoice`, permitindo que o assistente comunique-se com o usuário de forma audível.

2. **Sistema de Recomendação:**
   - **Análise de Dados:** Utiliza um dataset armazenado em um arquivo CSV que contém informações sobre produtos, suas categorias e descrições. Esse dataset é lido e filtrado para fornecer recomendações relevantes.
   - **Geração de Recomendação:** Com base no comando do usuário solicitando recomendações, o sistema consulta o dataset para encontrar produtos que correspondam à categoria mencionada e gera uma resposta com essas informações.

### Justificativa da Escolha da Arquitetura

- **Eficiência e Precisão:** O uso de `speech_recognition` e `responsiveVoice` garante uma comunicação fluida e natural. O modelo Gemini oferece respostas contextuais apropriadas e humanizadas.
- **Flexibilidade:** A arquitetura permite ajustes fáceis no modelo Gemini e manutenção simples do dataset CSV.
- **Acessibilidade:** Projetada para ser acessível a pessoas com deficiência visual, facilitando a interação através de comandos de voz.
- **Personalização:** O sistema de recomendação fornece sugestões específicas baseadas nas preferências do usuário, melhorando a experiência e a satisfação.

