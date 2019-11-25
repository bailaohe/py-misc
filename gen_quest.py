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
    """DocxExporter"""
    def open(self, path, columns=2):
        """open the docx exporter

        :param path: the path to dump docx file
        :param columns: the columns of exported docx file
        """
        doc = Document()
        qtable = doc.add_table(rows=0, cols=columns)
        return (doc, qtable, path)

    def write(self, handle, qrow):
        """write the question row into the docx handle

        :param handle: the handle of open handle of docx exporter
        :param qrow: the question row
        """
        (_, qtable, _) = handle
        qcells = qtable.add_row().cells
        for qid, qtext in enumerate(qrow):
            qcells[qid].text = qtext

    def close(self, handle):
        """close the handle of docx handle

        :param handle: the handle
        """
        (doc, _, path) = handle
        doc.save(path)

class PlainExporter(object):
    """PlainExporter"""
    EXPR_WIDTH = 11
    LINE_WIDTH = 84

    def open(self, path, columns=2):
        """open the plain exporter

        :param path: the path (useless)
        :param columns: the columns to dump questions
        """
        return (columns,)

    def write(self, handle, qrow):
        """write the question row

        :param handle: the plain handle
        :param qrow: the question row
        """
        (columns,) = handle
        qline = ''
        for qid in range(columns - 1):
            qline += qrow[qid]
            qline += ' ' * int(PlainExporter.LINE_WIDTH / columns - PlainExporter.EXPR_WIDTH)
        qline += qrow[columns - 1]
        print(qline)

    def close(self, handle):
        """close the plain handle

        :param handle: the plain handle
        """
        pass

# the registerred exporters
EXPRORTERS = {
    'docx': DocxExporter,
    'doc': DocxExporter,
    'plain': PlainExporter,
}

@click.command()
@click.option('-c', '--columns', default=2, help='出题列数')
@click.option('-q', '--questions', default=100, help='出题数量')
@click.option('-e', '--export-format', default='plain', help='导出类型')
@click.option('-f', '--export-name', default='quest', help='导出文件名')
def gqcmd(columns, questions, export_format, export_name):
    """gqcmd the command entry to generate questions

    :param columns: the column count
    :param questions: the question count
    :param export_format: the export format
    :param export_name: the export file name
    """
    exporter = EXPRORTERS[export_format]()
    ehandle = exporter.open(export_name + '.' + export_format, columns=columns)

    # the row to hold questions in single row
    qrow = list()
    for q in gen_question(questions):
        qrow.append(q)
        # trigger the row dump whenever the it is *FULL*
        if len(qrow) >= columns:
            exporter.write(ehandle, qrow)
            qrow = list()
    exporter.close(ehandle)

if __name__ == '__main__':
    gqcmd()

