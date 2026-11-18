# Verificação desta entrega

- 10 testes automatizados passaram no Django 5.2.18.
- Migrações executadas com sucesso num banco separado.
- Três cursos demonstrativos e seis aulas criados pelo comando seed_demo.
- Verificação do Django sem erros de configuração local.
- Páginas de catálogo, cadastro, login, aluno e administração renderizadas pelo cliente de testes.

Cobertura: hash de senha, impedimento de promoção administrativa pelo cadastro, login, logout por POST, limite de tentativas, inscrição gratuita, bloqueio de inscrição paga, isolamento de progresso, proteção de rascunhos e aulas, criação de curso/aula, concessão de acesso, CSRF, escape de texto e geração de e-mail de recuperação.

Ainda não verificado: aparência num navegador real, instalação pelo iniciador no computador do usuário, entrega real de e-mails, hospedagem pública ou pagamentos. A recuperação por e-mail foi testada com uma caixa em memória; no modo local, o link é impresso no terminal.
