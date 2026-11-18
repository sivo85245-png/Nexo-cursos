# Nexo Cursos

Plataforma local funcional de cursos, com cadastro próprio por e-mail e senha, área do aluno e painel de publicação. Feita com Django e SQLite. Os cursos iniciais são textos introdutórios originais de demonstração, editáveis no Studio.

## Abrir no Windows

1. Extrai o ZIP inteiro para uma pasta. Não executes o projeto dentro do ZIP.
2. Instala Python 3.10 ou mais recente, marcando **Add Python to PATH**.
3. Abre **ABRIR_NEXO.bat** com dois cliques. Na primeira vez, é necessária internet para instalar Django.
4. O programa pede teu e-mail, nome e uma senha para criar o administrador. A senha não aparece enquanto escreves: é normal. Guarda esses dados.
5. O site abre no navegador em **http://127.0.0.1:8000/**. Mantém a janela do terminal aberta enquanto usas o site.

Se o navegador não abrir automaticamente, digita esse endereço. Para encerrar, pressiona Ctrl+C no terminal. Se houver erro, a janela fica aberta para poderes ler a mensagem.

## Usar no VS Code

Vai a **Arquivo → Abrir Pasta** e seleciona a pasta Nexo_Cursos que contém manage.py. Abre **Terminal → Novo Terminal** e executa:

```powershell
py -3 iniciar.py
```

O VS Code serve para editar; o site é usado pelo navegador. Não uses Live Server para este projeto, pois o login e os dados dependem do servidor Python.

## Publicar os teus cursos

Entra com a conta de administrador e clica em **Studio**. Cria um curso, define categoria, preço e descrição, guarda e adiciona aulas. Cada aula aceita texto, vídeo do YouTube/Vimeo e link HTTPS de material complementar. Os materiais são links externos, não uploads. Marca o curso e as aulas como publicados para que apareçam aos alunos. Desmarca para retirar do ar sem apagar inscrições.

Cria uma conta normal pelo botão **Começar agora** para testar como aluno. Cursos gratuitos permitem inscrição imediata. Cada aluno tem suas próprias conclusões e pode desfazê-las. O Studio também permite conceder acesso manual a uma conta já cadastrada.

## O que está pronto

- Catálogo com pesquisa, categorias e filtro de gratuitos.
- Cadastro, login por e-mail, logout e recuperação de senha.
- Senhas com hash do Django, sessões, CSRF e limitação de tentativas de login por conta.
- Inscrições gratuitas, aulas protegidas, progresso persistente e área do aluno.
- Studio de criação e edição de cursos e aulas, rascunhos e concessão de acesso.
- Layout responsivo, sem dependências de fontes ou imagens externas.
- Três cursos iniciais: dois gratuitos e um exemplo pago com venda desativada.

## Limites desta entrega

O site roda no teu computador; ainda não está publicado na internet. Pagamentos reais, confirmação de e-mail, certificados, uploads de arquivos e envio real de e-mails ainda não estão configurados. No modo local, o link de recuperação de senha aparece no terminal, não na caixa de e-mail. Os vídeos externos só carregam ao abrir uma aula que tenha vídeo configurado.

Os preços estão em reais e podem ser editados. Para cobrar, falta integrar teu provedor de pagamento e validar as notificações de pagamento no servidor antes de liberar acesso. O valor exibido não inicia cobrança. Usa conteúdos próprios ou materiais para os quais tenhas autorização compatível com o uso pretendido; um curso ser gratuito não é autorização para copiá-lo ou revendê-lo.

## Dados e cópia de segurança

Contas, aulas e progresso ficam em **db.sqlite3**, criado na primeira execução. Faz uma cópia desse arquivo com o servidor parado. A chave local fica em **.local-secret**. Não publiques esses arquivos nem compartilhes um ZIP contendo dados dos alunos. O ZIP entregue não inclui contas nem senhas.

O comando seed_demo não sobrescreve cursos existentes. Para não usar exemplos numa nova instalação, executa migrate manualmente e não executes seed_demo; ajusta também iniciar.py, que chama esse comando.

## Testar

Depois da primeira instalação:

```powershell
.\.venv\Scripts\python.exe manage.py test
```

Os testes usam um banco temporário e verificam autenticação, permissões, publicação, proteção de aulas, CSRF, recuperação de senha e separação do progresso.

## Próxima etapa: hospedagem

Esta versão usa login próprio, sem depender de contas ChatGPT. Para publicar, escolhe uma hospedagem Python com armazenamento persistente. Define as variáveis descritas em **.env.example** no ambiente do servidor; esse arquivo não é carregado automaticamente. Usa NEXO_ENV=production, uma chave aleatória exclusiva, domínio permitido, HTTPS, SMTP e backups. Não uses runserver na internet.

Em um servidor Linux, instala requirements.txt, executa migrate, collectstatic e createsuperuser. Inicia **gunicorn config.wsgi:application**, atrás de um proxy HTTPS configurado corretamente. Serve /static/ a partir de staticfiles. Configura a comunicação HTTPS/proxy para que o Django reconheça requisições seguras, conforme a documentação da hospedagem; não confies em cabeçalhos encaminhados de origens arbitrárias. Para tráfego maior, migra SQLite para PostgreSQL e reforça a limitação de acesso no proxy. Revisa privacidade, termos, autorização de materiais, recuperação por e-mail e pagamentos antes de abrir inscrições públicas.

Não há senha administrativa padrão nem credenciais de pagamento no código.
