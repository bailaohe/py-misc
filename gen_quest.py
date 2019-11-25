import random
import time
import click
from docx import Document

OP_TABLE = ['+', '-', '×', '÷']

def gen_question(qnum: int):
    """gen_question

    :param qnum: the count to questions
    :type qnum: int
    """
    random.seed(time.time())
    for i in range(qnum):
        first = random.randint(0, 10)
        op = OP_TABLE[random.randint(0, 1)]
        if op == '+':
            second = random.randint(first, 10) - first
        elif op == '-':
            second = random.randint(0, first)
        yield '%2d %1s%2d =' % (first, op, second)

class DocxExporter(object):
    def open(self, path, columns=2):
        doc = Document()
        qtable = doc.add_table(rows=0, cols=columns)
        return (doc, qtable, path)

    def write(self, handle, qrow):
        (_, qtable, _) = handle
        qcells = qtable.add_row().cells
        for qid, qtext in enumerate(qrow):
            qcells[qid].text = qtext

    def close(self, handle):
        (doc, _, path) = handle
        doc.save(path)

class PlainExporter(object):
    EXPR_WIDTH = 11
    LINE_WIDTH = 84

    def open(self, path, columns=2):
        return (columns,)

    def write(self, handle, qrow):
        (columns,) = handle
        qline = ''
        for qid in range(columns - 1):
            qline += qrow[qid]
            qline += ' ' * int(PlainExporter.LINE_WIDTH / columns - PlainExporter.EXPR_WIDTH)
        qline += qrow[columns - 1]
        print(qline)

    def close(self, handle):
        pass

EXPRORTERS = {
    'docx': DocxExporter,
    'doc': DocxExporter,
    'plain': PlainExporter,
}

@click.command()
@click.option('-c', '--columns', default=2, help='出题列数')
@click.option('-q', '--question-count', default=100, help='出题数量')
@click.option('-e', '--export-format', default='plain', help='导出类型')
@click.option('-f', '--export-name', default='quest', help='导出文件名')
def gqcmd(columns, question_count, export_format, export_name):
    exporter = EXPRORTERS[export_format]()
    ehandle = exporter.open(export_name + '.' + export_format, columns=columns)

    qrow = list()
    for q in gen_question(question_count):
        qrow.append(q)
        if len(qrow) >= columns:
            exporter.write(ehandle, qrow)
            qrow = list()
    exporter.close(ehandle)

if __name__ == '__main__':
    gqcmd()

