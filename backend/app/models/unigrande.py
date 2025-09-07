from tortoise import fields, models
from datetime import date
from decimal import Decimal

# ------------- TABELAS DE APOIO ----------------------
class PeriodoLetivo(models.Model):
    """
    Representa um semestre acadêmico específico, como 2025.1. \n
    Armazena o ano, o semestre e as datas de início e fim.
    """

    id: int = fields.IntField(pk=True)
    ano: int = fields.IntField() # O ano que pode ser 2020, 2025
    semestre: int = fields.IntField() # Semestre que pode ser 1, 2, 3...
    data_inicio: "date | None" = fields.DateField(null=True)
    data_fim: "date | None" = fields.DateField(null=True)

    class Meta:
        table = "periodos_letivos"
        unique_together = (("ano", "semestre"),)
        indexes = (("ano", "semestre"),)

    def __str__(self) -> str:
        return f"{self.ano}.{self.semestre}"

class Professor(models.Model):
    """
    Representa um docente cadastrado no sistema da universidade. \n
    Armazena informações de identificação como matrícula e nome,
    e pode ser vinculado como coordenador de Cursos ou professor de Turmas.
    """

    id: int = fields.IntField(pk=True)
    matricula: int = fields.IntField(null=True)
    nome_professor: str = fields.CharField()
    endereco_professor: str = fields.CharField()
    email_professor: str = fields.CharField()

    class Meta:
        table = "professores"
        indexes = ("nome",)

    def __str__(self) -> str:
        return self.nome

class Curso(models.Model):
    """
    São os Cursos da Universidade. \n
    Armazena informações importantes sobre cada curso, e possui
    relação com Coordenador/Professor 
    """
    id: int = fields.IntField(pk=True) # Código do Curso
    nome: str = fields.CharField(max_length=40)
    total_creditos: int = fields.IntField()
    coordenador: "Professor | None" = fields.ForeignKeyField(
        "models.Professor",
        related_name="cursos_coordenados",
        null=True,  # pode não existir ainda
        on_delete=fields.CASCADE,
        source_field="idt_prof",  # mantém a ideia do ER
    )

    class Meta:
        table = "cursos"
        indexes = ("nome",)

    def __str__(self) -> str:
        if self.coordenador:
            # Se existir um coordenador, mostre o nome do curso e do coordenador
            return f"{self.nome} (Coord: {self.coordenador.nome})"
        else:
            # Se não houver coordenador, mostre apenas o nome do curso
            return self.nome

class Disciplina(models.Model):
    """
    São as disciplinas do Curso. \n
    Apresenta suas características, incluindo
    se é obrigatória ou eletiva, junto das horas
    """
    id: int = fields.IntField(pk=True) # Código Disciplina
    nome: str = fields.CharField(max_length=50)
    creditos: int = fields.IntField()
    tipo: str = fields.CharField(max_length=1) # 'O' obrigatória, 'E' eletiva, etc.
    horas_obrigatorias: int = fields.IntField()
    limite_faltas: int = fields.IntField()

    class Meta:
        table = "disciplinas"
        indexes = ("nome",)

    def __str__(self) -> str:
        # Cria um dicionário para mapear o tipo a uma palavra completa
        tipos_disciplina = {
            'O': 'Obrigatória',
            'E': 'Eletiva',
        }
        # Usa o dicionário para pegar a descrição do tipo, com um valor padrão caso não encontre
        tipo_descritivo = tipos_disciplina.get(self.tipo, 'Desconhecido')

        return f"{self.nome} ({self.creditos} créditos - {tipo_descritivo})"

class Matriz(models.Model):
    """
    Currículo, qual disciplina pertence a qual curso e em qual período. 
    """
    id: int = fields.IntField(pk=True) # codigo_disciplina
    curso: "Curso" = fields.ForeignKeyField(
        "models.Curso",
        related_name="matrizes"
    )
    disciplina: "Disciplina" = fields.ForeignKeyField(
        "models.Disciplina",
        related_name="matrizes",
    )
    periodo: int = fields.IntField() # período/semestre no currículo

    class Meta:
        table = "matrizes"
        unique_together = (("curso", "disciplina"),)
        indexes = (("curso_id", "periodo"),)

    def __str__(self) -> str:
        curso_nome = self.curso.nome if self.curso else "Curso não definido"
        disciplina_nome = self.disciplina.nome if self.disciplina else "Disciplina não definida"

        return f"{curso_nome} - {disciplina_nome} ({self.periodo}º período)"

class Turma(models.Model):
    """
    São as Turmas, oferta da disciplina no período letivo, com professor e vagas. \n
    """
    id: int = fields.IntField(pk=True)
    periodo_letivo: "PeriodoLetivo" = fields.ForeignKeyField(
        "models.PeriodoLetivo",
        related_name="turmas",
    )
    curso: "Curso" = fields.ForeignKeyField(
        "models.Curso",
        related_name="turmas",
    )
    disciplina: "Disciplina" = fields.ForeignKeyField(
        "models.Disciplina",
        related_name="turmas",
    )
    professor: "Professor | None" = fields.ForeignKeyField(
        "models.Professor",
        related_name="turmas",
        null=True
    )
    vagas: int = fields.IntField(default=0)

    class Meta:
        table = "turmas"
        # evita duplicar oferta da mesma disciplina no mesmo PL/curso
        unique_together = (("periodo_letivo", "curso", "disciplina"),)
        indexes = (("periodo_letivo_id", "curso_id"),)

    def __str__(self) -> str:
      info_disciplina = self.disciplina.nome if self.disciplina else "Disciplina Indefinida"
      
      info_periodo = str(self.periodo_letivo) if self.periodo_letivo else "Período Indefinido"

      representacao = f"{info_disciplina} - Turma de {info_periodo}"

      if self.professor:
        representacao += f" (Prof: {self.professor.nome})"

        return representacao

# --------- ALUNOS, HISTÓRICO, MATRÍCULAS -------------
class Aluno(models.Model):
    """
    Aluno, com todos seus atributos e conexões.
    """
    matricula: int = fields.IntField(pk=True) # matricula aluno
    nome: str = fields.CharField(max_length=50)
    total_creditos: int = fields.IntField()
    data_nascimento: date = fields.DateField()
    mgp: "Decimal | None" = fields.DecimalField(max_digits=5, decimal_places=2, null=True)
    curso: "Curso" = fields.ForeignKeyField(
        "models.Curso",
        related_name="alunos",
    )

    class Meta:
        table = "alunos"
        indexes = ("nome", "curso_id")

    def __str__(self) -> str:
        curso_nome = self.curso.nome if self.curso else "Curso não definido"
        return f"{self.nome} - {curso_nome}"

class Matricula(models.Model):
    """
    Matrícula do Aluno, com suas respectivas notas e faltas
    """
    id: int = fields.IntField(pk=True)
    aluno: "Aluno" = fields.ForeignKeyField(
        "models.Aluno", related_name="matriculas",
    )
    turma: "Turma" = fields.ForeignKeyField(
        "models.Turma", related_name="matriculas",        
    )
    # Notas (até 3 avaliações) e faltas por avaliação
    nota_01: "Decimal | None" = fields.DecimalField(max_digit=5, decimal_places=2, null=True)
    nota_02: "Decimal | None" = fields.DecimalField(max_digit=5, decimal_places=2, null=True)
    nota_03: "Decimal | None" = fields.DecimalField(max_digit=5, decimal_places=2, null=True)
    faltas_01: "int | None" = fields.IntField(null=True)
    faltas_02: "int | None" = fields.IntField(null=True)
    faltas_03: "int | None" = fields.IntField(null=True)

    class Meta:
        table = "matriculas"
        unique_together = (("aluno", "turma"),)
        indexes = (("aluno_id", "turma_id"),)

    def __str__(self) -> str:
        aluno_nome = self.aluno.nome if self.aluno else "Aluno não registrado"

        return f"{aluno_nome} ({self.id})"
    
class Historico(models.Model):
    """
    Resultado final do aluno em uma disciplina em um ano/semestre
    """
    id: int = fields.IntField(pk=True)
    periodo_letivo: "PeriodoLetivo" = fields.ForeignKeyField(
        "models.PeriodoLetivo", related_name="historicos"
    )
    disciplina: "Disciplina" = fields.ForeignKeyField(
        "models.Disciplina", related_name="historicos"
    )
    aluno: "Aluno" = fields.ForeignKeyField(
        "models.Aluno", related_name="historicos"
    )
    situacao: str = fields.CharField(max_length=2) # AP/RE/TC/MT, etc.
    media_final: float = fields.DecimalField(max_digits=5, decimal_places=2, null=True)
    faltas: "int | None" = fields.IntField(null=True)

    class Meta:
        table = "historicos"
        unique_together = (("periodo_letivo", "aluno", "disciplina"),)
        indexes = (("aluno_id", "periodo_letivo_id"),)

    def __str__(self) -> str:
      nome_aluno = self.aluno.nome if self.aluno else "Aluno inválido"
      nome_disciplina = self.disciplina.nome if self.disciplina else "Disciplina inválida"
        
      return f"Histórico de {nome_aluno} em {nome_disciplina}: {self.situacao}"