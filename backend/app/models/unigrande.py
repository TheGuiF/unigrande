from tortoise import fields, models
from datetime import datetime

class PeriodoLetivo(models.Model):
    id: int = fields.IntField(pk=True)
    ano: int = fields.IntField() # O ano que pode ser 2020, 2025
    semestre: int = fields.IntField() # Semestre que pode ser 1, 2, 3...
    data_inicio: datetime = fields.DateField()
    data_fim: datetime = fields.DateField()

    class Meta:
        table = "periodos_letivos"
        unique_together = (("ano", "semestre"),)
        indexes = (("ano", "semestre"),)

class Professor(models.Model):
    idt_professor: int = fields.IntField(pk=True)
    matricula_professor: int = fields.IntField()
    nome_professor: str = fields.CharField()
    endereco_professor: str = fields.CharField()
    email_professor: str = fields.CharField()

    class Meta:
        table = "professores"


class Curso(models.Model):
    codigo_curso: int = fields.IntField(pk=True)
    nome_curso: str = fields.CharField(40)
    tot_cred: int = fields.IntField()
    idt_professor: int = fields.IntField(fk=True)

    class Meta:
        table: "cursos"

class Disciplina(models.Model):
    codigo_disciplina: int = fields.IntField(pk=True)
    nome_disciplina: str = fields.CharField(50)
    creditos: int = fields.IntField()
    tipo_disciplina: str = fieldsCharField()
    horas_obrigatorias: int = fields.IntField()
    limite_faltas: int = fields.IntField()

    class Meta:
        table: "disciplinas"

class Matriz(models.Model):
    codigo_disciplina: int = fields.IntField(fk=True)
    codigo_curso: int = fields.IntField(fk=True)
    periodo: int = fields.IntField()

    class Meta:
        table: "matrizes"

class Turma(models.Model):
    ano: int = fields.IntField(fk=True)
    semestre: int = fields.IntField(fk=True)
    codigo_disciplina: int = fields.IntField(fk=True)
    vagas: int = fields.IntField()
    idt_professor: int = fields.IntField(fk=True)

    class Meta:
        table: "turmas"

class Aluno(models.Model):
    matricula_aluno_id: int = fields.IntField(pk=True)
    nome_aluno: str = fields.CharField(30)
    tot_cred_aluno: int = fields.IntField(3)
    data_nascimento: datetime = fields.DateField()
    mgp_decimal: float = fields.DecimalField(4,2)
    codigo_curso: int = fields.IntField(fk=True)

    class Meta:
        table = "alunos"

class Matricula(models.Model):
    ano: int = fields.IntField(fk=True)
    semestre: int = fields.IntField(fk=True)
    matricula_aluno_id: int = fields.IntField(fk=True)
    codigo_disciplina: int = fields.IntField(fk=True)
    nota_01: float = fields.DecimalField()
    nota_02: float = fields.DecimalField()
    nota_03: float = fields.DecimalField()
    faltas_01: int = fields.IntField()
    faltas_02: int = fields.IntField()
    faltas_03: int = fields.IntField()

    class Meta:
        table: "matriculas"

class Historico(models.Model):
    ano: int = fields.IntField(fk=True)
    semestre: int = fields.IntField(fk=True)
    codigo_disciplina: int = fields.IntField(fk=True)
    matricula_aluno_id: int = fields.IntField(fk=True)
    situacao: str = fields.CharField()
    media: float = fields.DecimalField()
    faltas: int = fields.IntField()

    class Meta:
        table: "historicos"