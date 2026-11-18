from django.core.management.base import BaseCommand
from academy.models import Course, Lesson

COURSES = [
    ('python-primeiros-passos', 'Python: do zero ao primeiro programa', 'tecnologia', 'purple', 0,
     'Uma introdução original e prática a variáveis, decisões e pequenos programas. Começa mesmo sem experiência.', [
        ('O que é um programa?', 'Um programa é uma sequência de instruções que o computador executa. Em Python, podemos escrever print("Olá, mundo!") para mostrar uma mensagem. O texto fica entre aspas e os parênteses indicam os dados enviados à função print.\n\nPensa numa receita: os passos precisam ser claros e estar numa ordem que faça sentido. Programar também exige testar se cada instrução produz o resultado esperado.\n\nPrática: num ambiente Python instalado no teu computador, executa print("Estou aprendendo Python"). Depois escreve outra linha que apresente o teu nome.\n\nVerificação: devem aparecer duas mensagens, uma por linha. Se surgir um erro, confere as aspas e os parênteses. Não copies as aspas curvas de um editor de texto.'),
        ('Variáveis e pequenas contas', 'Uma variável associa um nome a um valor. Escreve pontos = 10 e depois print(pontos). Para atualizar esse valor, usa pontos = pontos + 5. O resultado passa a ser 15.\n\nPython diferencia números e textos. O número 10 permite fazer contas; o texto "10" é uma sequência de caracteres. Usa nomes que expliquem o significado, como total_aulas, em vez de letras sem contexto.\n\nPrática: define preco = 20 e quantidade = 3. Calcula total = preco * quantidade e mostra o total.\n\nResposta esperada: 60. Agora altera a quantidade para 4 e executa outra vez. O total deve ser 80.'),
        ('Tomar decisões com if', 'Um programa pode escolher um caminho. O comando if executa um bloco quando uma condição é verdadeira. A indentação faz parte da sintaxe de Python: usa quatro espaços nas linhas dentro do bloco.\n\npontos = 80\nif pontos >= 60:\n    print("Meta atingida")\nelse:\n    print("Continua praticando")\n\nPrática: testa pontos com os valores 59, 60 e 80. Antes de executar, anota a mensagem que esperas ver.\n\nVerificação: 59 mostra "Continua praticando". Tanto 60 como 80 mostram "Meta atingida", porque >= inclui o valor limite. Esse teste de fronteira é uma boa prática para encontrar erros.\n\nDesafio final: cria uma variável aulas_concluidas e mostra uma mensagem especial quando ela chegar a 3.')]),
    ('aprender-com-metodo', 'Aprender a aprender: cria a tua rotina', 'estudos', 'green', 0,
     'Organiza uma rotina possível, pratica o que aprendes e acompanha a tua evolução com exercícios simples.', [
        ('Transforma uma intenção numa meta', '"Quero aprender programação" é uma intenção ampla. Uma meta de estudo útil descreve uma ação observável e um prazo possível: "Nesta semana, vou escrever e explicar três programas pequenos".\n\nEscolhe uma habilidade específica, reserva um período que caiba no teu dia e define uma entrega. Não precisas começar com horas de estudo; uma sessão curta e focada já permite realizar um exercício.\n\nPrática: completa a frase "Até sexta-feira vou conseguir ___ e vou demonstrar isso por meio de ___". Escolhe algo pequeno o suficiente para terminar.\n\nNo fim da semana, compara a entrega com a meta. Se não terminaste, ajusta o tamanho da tarefa ou o horário; usa o resultado para planejar a próxima tentativa.'),
        ('Estuda, explica e pratica', 'Depois de ler uma explicação, fecha o material e tenta descrever a ideia com as tuas palavras. Em seguida, resolve um exemplo sem olhar a resposta. A dificuldade que aparece indica o que precisas revisar.\n\nUma sessão pode ter três partes: conhecer uma ideia, aplicá-la num pequeno exercício e registrar a dúvida que restou. O tempo de cada etapa depende do assunto e da tua disponibilidade.\n\nPrática: escolhe uma aula deste site. Escreve três perguntas sobre ela, responde sem consultar o texto e depois compara. Corrige as respostas com uma cor diferente.\n\nPara a próxima sessão, começa pelas perguntas que não conseguiste responder. O objetivo é perceber o que sabes fazer, e não apenas contar páginas lidas.')]),
    ('ideia-a-projeto', 'Da ideia ao teu primeiro projeto', 'negocios', 'orange', 49.90,
     'Curso demonstrativo de uma futura oferta paga. A compra ainda não está disponível; preço e conteúdo podem ser editados no Studio.', [
        ('Define o problema antes da solução', 'Este é um conteúdo original de demonstração para configurar um curso pago.\n\nUm projeto começa com uma situação que queremos melhorar. Descreve quem tem o problema, em que momento ele aparece e qual é a consequência. Evita começar pela lista de funcionalidades.\n\nExemplo: um estudante guarda exercícios em várias pastas e demora para encontrar o que precisa revisar. Uma primeira entrega pode ser uma lista organizada por assunto, com pesquisa simples.\n\nPrática: descreve um problema que observas no teu dia. Conversa com alguém que também o enfrenta e registra um exemplo concreto. Depois define uma pequena entrega que possa ser testada. Não precisas construir a solução completa para aprender com essa primeira tentativa.')]),
]

class Command(BaseCommand):
    help = 'Adiciona cursos demonstrativos originais sem substituir os cursos existentes.'
    def handle(self, *args, **options):
        created_count = 0
        for slug, title, category, theme, price, description, lessons in COURSES:
            course, created = Course.objects.get_or_create(slug=slug, defaults=dict(title=title, category=category, theme=theme, price=price, description=description, published=True))
            if not created:
                continue
            created_count += 1
            for position, (name, content) in enumerate(lessons, 1):
                Lesson.objects.create(course=course, title=name, content=content, position=position, published=True)
        self.stdout.write(self.style.SUCCESS(f'{created_count} cursos de demonstração adicionados.'))
